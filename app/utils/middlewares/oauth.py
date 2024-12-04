import json
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwe, jwt
from sqlalchemy.orm import Session

from app.common import constants
from app.config import env_variables
from app.database import db_connection
from app.features.aws.secretKey import get_secret_keys
from app.models.forms import Forms
from app.models.user import User
from app.models.user_details import UserDetails
from app.models.user_sessions import UserSession

env_data = env_variables()
keys = get_secret_keys()


security = HTTPBearer()


def update_user_forms(user_id: int, db: Session):
    try:
        # Fetch user and forms in one go
        user = db.query(User).filter(User.id == user_id).first()
        user = user.to_dict()
        user_details = (
            db.query(UserDetails)
            .filter(UserDetails.user_id == user_id)
            .first()
        )

        if not user_details:
            # Create a new UserDetails record if it doesn't exist
            user_details = UserDetails(user_id=user_id, profile_summary=None)
            db.add(user_details)
            db.flush()

        # Fetch enabled forms
        forms = (
            db.query(Forms).order_by(Forms.id).filter(
                Forms.is_enabled == True).all()
        )
        if not forms:
            return

        # If the user has no existing profile summary, create a new one
        if not user_details.to_dict().get("profile_summary"):
            user_details.profile_summary = json.dumps(
                [
                    [
                        {
                            "field_id": field["field_id"],
                            "field_name": field["field_name"],
                            "is_enabled": field["is_enabled"],
                            "form_group_id": field["form_group_id"],
                            "inner_group_id": field["form_group_id"],
                            "value": "",
                        }
                        for group in f.to_dict().get("form_groups", [])
                        for field in group.get("fields", [])
                    ]
                    for f in forms
                ]
            )
            return

        # Update the existing profile summary
        profile_summary_data = (
            json.loads(user_details.profile_summary)
            if user_details.profile_summary
            else []
        )
        current_profile_summary = []

        for i, f in enumerate(forms):
            formgroup = [
                {
                    "field_id": field["field_id"],
                    "field_name": field["field_name"],
                    "is_enabled": field["is_enabled"],
                    "form_group_id": field["form_group_id"],
                    "inner_group_id": group["form_group_id"],
                    "value": "",
                }
                for group in f.to_dict().get("form_groups", [])
                for field in group.get("fields", [])
            ]

            # Retrieve current profile data for the current form if it exists
            current_data = (
                profile_summary_data[i] if i < len(profile_summary_data) else []
            )
            field_value_map = {item["field_id"]: item for item in current_data}

            # Update or add fields in the current profile data
            for field in formgroup:
                if field["field_id"] in field_value_map:
                    # Update existing field's `is_enabled`
                    field_value_map[field["field_id"]]["is_enabled"] = field[
                        "is_enabled"
                    ]
                else:
                    # Add new field if it doesn't exist
                    current_data.append(
                        {
                            "field_name": field["field_name"],
                            "field_id": field["field_id"],
                            "value": "",
                            "form_group_id": (
                                current_data[0]["form_group_id"]
                                if current_data[0]["form_group_id"]
                                else None
                            ),
                            "inner_group_id": field["inner_group_id"],
                            "is_enabled": field["is_enabled"],
                        }
                    )

            # Filter out any fields not in the current formgroup
            field_ids_in_formgroup = {field["field_id"] for field in formgroup}
            current_data = [
                field
                for field in current_data
                if field["field_id"] in field_ids_in_formgroup
            ]

            current_profile_summary.append(current_data)
        user_details.profile_summary = json.dumps(current_profile_summary)
        db.commit()
    except Exception as e:
        db.rollback()
        print("Error while updating user forms:", e)


async def is_user_authorized(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(db_connection),
) -> dict:
    try:
        token = credentials.credentials
        jwt_token = jwe.decrypt(token, "asecret128bitkey")

        payload = jwt.decode(
            jwt_token, keys["SECRET_KEY"], algorithms=keys["ALGORITHM"]
        )

        # current_time = int(time.time())
        # now = datetime.utcnow()
        id = payload.get("id")
        email = payload.get("email")
        account_type = payload.get("account_type")

        if not id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": constants.ACCESS_DENIED},
            )

        user = db.query(User).get(id)
        user_session = (
            db.query(UserSession)
            .filter(UserSession.user_id == id, UserSession.token == token)
            .first()
        )

        if user_session is None:
            raise ValueError(constants.TOKEN_NOT_FOUND)
        # if payload["exp"] <= current_time:
        #     raise ValueError(constants.SESSION_EXPIRED)

        if not user:
            raise ValueError(constants.USER_NOT_FOUND)

        if not user.is_active:
            raise ValueError(constants.USER_INACTIVE)

        if not user.is_verified:
            raise ValueError(constants.USER_NOT_VERIFIED)

        # if now > datetime.fromtimestamp(payload.get("exp")):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail={"error": constants.INVALID_TOKEN},
        #     )

        return user.to_dict()
    except Exception as e:
        print(e, "Exception")
        error_message = str(e)
        if error_message == constants.USER_INACTIVE:
            detail = constants.USER_INACTIVE
        else:
            detail = constants.INVALID_TOKEN

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": detail},
        )

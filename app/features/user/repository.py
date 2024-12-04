import bcrypt

import json

# import bcrypt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from app.models.forms import Forms
from app.models.journal import Journal
from app.utils.helper.helper_functions import format_datetime_custom

from sqlalchemy.orm import Session
from sqlalchemy import and_, bindparam, func, or_

from app.common import constants
from app.features.auth.utils import verify_password
from app.features.user.schemas import (
    AccountDeleteSchema,
    CurrentUser,
    SetQuestionsCountSchema,
    UpdatePasswordSchema,
    UpdateUserDetails,
    UserDetailsSchema,
    UserProfileSchema,
)
from app.models.user import User
from app.models.questions import Questions
from app.models.user_details import UserDetails


# Add user details


async def add_user_details(
    request: UserDetailsSchema, db: Session, current_user: CurrentUser
):
    logged_user_id = current_user["id"]

    try:
        existing_details = (
            db.query(UserDetails).filter(UserDetails.user_id == logged_user_id).first()
        )
        form_data = [data.dict() for data in request.profile_summary]
        if not existing_details:

            new_user_details = UserDetails(
                user_id=logged_user_id,
                profile_summary=json.dumps([form_data]),
            )
            db.add(new_user_details)
            db.commit()
            db.refresh(new_user_details)

            return {
                "message": constants.USER_DETAIL_SUCCESS,
                "success": True,
                "data": current_user,
            }

        # Load the existing profile_summary (convert from JSON string to Python list)
        profile_summary_data = (
            json.loads(existing_details.profile_summary)
            if existing_details.profile_summary
            else []
        )
        if not isinstance(profile_summary_data, list):
            profile_summary_data = []
        # Handle update or append
        if request.update_index is not None:
            if request.update_index < len(profile_summary_data):
                # Update at the provided index
                profile_summary_data[request.update_index] = [
                    data.dict() for data in request.profile_summary
                ]
            else:
                # Append to the list if index is greater than current length
                profile_summary_data.append(
                    [data.dict() for data in request.profile_summary]
                )

        else:
            return {
                "message": "No index provided",
                "success": False,
            }

        # Update the user's profile summary with the modified data and convert it back to JSON
        existing_details.profile_summary = json.dumps(profile_summary_data)
        db.commit()

        return {
            "message": constants.USER_DETAIL_SUCCESS,
            "success": True,
            "data": current_user,
        }

    except Exception as e:
        print("Error in adding user details:", e)
        return {
            "message": constants.INTERNAL_SERVER_ERROR,
            "success": False,
        }


async def get_form_values(form_id: int, db: Session, current_user: CurrentUser):
    logged_user_id = current_user["id"]
    form_id = int(form_id)
    try:
        existing_details = (
            db.query(UserDetails).filter(UserDetails.user_id == logged_user_id).first()
        )
        profile_summary_data = (
            json.loads(existing_details.profile_summary)
            if existing_details.profile_summary
            else []
        )
        return {
            "message": constants.FORM_FETCHED,
            "success": True,
            "data": profile_summary_data[form_id],
        }
    except Exception as e:
        print("error in accessing the form", e)
        return {
            "message": constants.INTERNAL_SERVER_ERROR,
            "success": False,
            "data": [],
        }


# Get user details
async def get_user_details(db: Session, current_user: CurrentUser):
    try:
        user_details = (
            db.query(UserDetails)
            .filter(UserDetails.user_id == current_user["id"])
            .first()
        )

        if not user_details:
            # Create a new UserDetails record if it doesn't exist
            user_details = UserDetails(user_id=current_user["id"], profile_summary=None)
            db.add(user_details)
            db.commit()
            db.flush()

        # Fetch enabled forms
        forms = (
            db.query(Forms).order_by(Forms.id).filter(Forms.is_enabled == True).all()
        )
        if not forms:
            return {"message": constants.FORM_NOT_FOUND, "success": False}

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
            db.commit()
            data = {
                "first_name": current_user.get("first_name", ""),
                "last_name": current_user.get("last_name", ""),
                "field_of_study": None,
                "dob": None,
                "gender": None,
                "address": None,
                "phone": None,
                "profile_summary": json.loads(user_details.profile_summary),
            }

            return {
                "message": constants.USER_DETAILS_FETCHED,
                "success": True,
                "data": data,
            }

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
        data = {
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "field_of_study": current_user["user_detail"]["field_of_study"],
            "dob": current_user["user_detail"]["dob"],
            "gender": current_user["user_detail"]["gender"],
            "address": current_user["user_detail"]["address"],
            "phone": current_user["phone"],
            "profile_summary": current_profile_summary,
        }
        return {"message": constants.FORM_FETCHED, "success": True, "data": data}

    except Exception as e:
        print("Error in getting user details:", e)
        return {
            "message": constants.INTERNAL_SERVER_ERROR,
            "success": False,
            "data": [],
        }


# Add education and work history


async def user_profile_update(
    request: UserProfileSchema, db: Session, current_user: CurrentUser
):
    try:
        user = db.query(User).filter(User.id == current_user["id"]).first()
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.phone = request.phone

        current_user["first_name"] = request.first_name
        current_user["last_name"] = request.last_name
        current_user["phone"] = request.phone
        # current_user["country_code"] = request.country_code
        if request.image:
            current_user["image"] = request.image
        # Check if user_details already exist for the given user_id
        existing_user_details = (
            db.query(UserDetails)
            .filter(UserDetails.user_id == current_user["id"])
            .first()
        )
        db.commit()
        if existing_user_details:
            existing_user_details.address = request.address
            existing_user_details.gender = request.gender
            existing_user_details.dob = request.dob
        else:
            new_user_details = UserDetails(
                user_id=current_user["id"],
                address=request.address,
                gender=request.gender,
                dob=request.dob,
            )
            # Add the new user to the database
            db.add(new_user_details)
            db.flush()  # Ensure the instance is persisted
            db.refresh(new_user_details)

        return {
            "message": constants.PROFILE_UPDATE_SUCCESSFULLY,
            "success": True,
            "data": {"user": request},
        }
    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def upload_user_profile_image(url: str, db: Session, user_id: int):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }
        user.image = url

        return {
            "message": constants.PROFILE_UPDATE_SUCCESSFULLY,
            "success": True,
            "data": {"user": user.to_dict()},
        }
    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def update_user_password(
    request: UpdatePasswordSchema, db: Session, user_id: int
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }
        if not verify_password(request.password, user.password):
            return {
                "message": constants.INCORRECT_OLD_PASSWORD,
                "success": False,
            }

        user.password = bcrypt.hash(
            request.new_password
        )  # Ensure the password is stored as a string

        # Commit the changes to the database

        return {
            "message": constants.PASSWORD_RESET_SUCCESSFULLY,
            "success": True,
        }
    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def user_account_delete(
    request: AccountDeleteSchema, db: Session, current_user: CurrentUser
):
    try:
        if (
            not current_user["account_type"] == "admin"
            and request.user_id
            and request.user_id != current_user["id"]
        ):
            return {
                "message": constants.USER_NOT_AUTHORIZE,
                "success": False,
            }

        user_id_to_delete = (
            request.user_id
            if current_user["account_type"] == "admin"
            else current_user["id"]
        )
        user = db.query(User).filter(User.id == user_id_to_delete).first()

        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }

        db.delete(user)

        return {
            "message": constants.ACCCOUNT_DELETE_SUCCESSFULLY,
            "success": True,
        }

    except Exception as e:
        # Log the exception properly
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def set_questions_count(
    request: SetQuestionsCountSchema, db: Session, current_user: CurrentUser
):
    try:
        existing_details = (
            db.query(UserDetails)
            .filter(UserDetails.user_id == current_user["id"])
            .first()
        )
        if existing_details:
            existing_details.question_set = request.count

            return {
                "message": constants.QUESTIONS_COUNT_UPDATED,
                "success": True,
            }
        new_user_details = UserDetails(
            question_set=request.count, user_id=current_user["id"]
        )

        db.add(new_user_details)

        db.refresh(new_user_details)
        return {
            "message": constants.QUESTIONS_COUNT_SUCCESS,
            "success": True,
        }
    except Exception as e:
        # Log the exception properly
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }


async def dashboard_details(db: Session):
    try:

        now = datetime.now()
        start_of_this_month = datetime(now.year, now.month, 1)
        start_of_last_month = start_of_this_month - timedelta(days=1)
        start_of_last_month = datetime(
            start_of_last_month.year, start_of_last_month.month, 1
        )
        now = datetime.now()
        one_week_ago = datetime.now() - timedelta(weeks=1)
        start_of_this_month = datetime(now.year, now.month, 1)
        end_date = datetime.combine(datetime.today(), datetime.max.time())
        start_date = (end_date - timedelta(days=6)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        total_journal_count = db.query(Journal).count()
        counts_query = db.query(
            func.count(User.id).label("total_users"),
            func.count()
            .filter(User.last_login >= start_of_this_month)
            .label("this_month_login_number"),
            func.count(User.id)
            .filter(
                User.last_login >= start_of_last_month,
                User.last_login < start_of_this_month,
            )
            .label("last_month_login_number"),
            func.count().filter(User.is_active == True).label("total_active_users"),
            func.count()
            .filter(User.created_ts >= one_week_ago)
            .label("total_new_weekly_signups"),
        ).first()

        last_month_login_number = 1
        if counts_query.last_month_login_number == 0:

            last_month_login_number = 1
        else:
            last_month_login_number = counts_query.last_month_login_number

        # Query to get the number of users who logged in during this month

        percentage_more_user_than_previous_month = (
            (counts_query.this_month_login_number - last_month_login_number)
            / last_month_login_number
        ) * 100

        users_by_joining_date = (
            db.query(
                func.count().label("user_count"),
                func.date(User.created_ts).label("date"),
            )
            .filter(User.created_ts >= start_date, User.created_ts <= end_date)
            .group_by(func.date(User.created_ts))
            .order_by(func.date(User.created_ts))
            .all()
        )
        index = 0
        data = []
        for day in range(start_date.day, end_date.day + 1):
            if (
                index < len(users_by_joining_date)
                and users_by_joining_date[index].date.day == day
            ):
                data.append(users_by_joining_date[index].user_count)
                index += 1
            else:
                data.append(0)

        return {
            "message": "User Dashboard Details",
            "success": True,
            "data": {
                "total_users": counts_query.total_users,
                "total_active_users": counts_query.total_active_users,
                "total_new_weekly_signups": counts_query.total_new_weekly_signups,
                "percentage_more_user_than_previous_month": percentage_more_user_than_previous_month,
                "total_journal_count": total_journal_count,
                "daily_signups_per_day_of_week": data,
            },
        }

    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def get_all_users(
    db: Session, offset: int, limit: int, searchQuery: str, loggedUserId: int
):
    try:
        all_users_query = (
            db.query(
                User.id,
                User.first_name,
                User.last_name,
                User.phone,
                User.email,
                User.image,
                User.is_active,
                User.last_login,
                User.created_ts,
            )
            .filter(
                and_(
                    or_(
                        User.first_name.op("~")(bindparam("search_query")),
                        User.last_name.op("~")(bindparam("search_query")),
                        User.email.op("~")(bindparam("search_query")),
                    ),
                    User.id != bindparam("logged_user_id"),
                )
            )
            .offset(offset)
            .limit(limit)
        )

        # Define the parameter values
        query_params = {"search_query": searchQuery, "logged_user_id": loggedUserId}

        # Execute the query with bound parameters
        all_users = all_users_query.params(**query_params).all()

        # Construct the response with only the needed fields
        users_data = [
            {
                "id": user.id,
                "full_name": f"{user.first_name} {user.last_name}",
                "phone": user.phone if user.phone else "N/A",
                "email": user.email if user.email else "N/A",
                "image": user.image,
                "is_active": user.is_active,
                "last_login": (
                    format_datetime_custom(user.last_login)
                    if user.last_login
                    else "N/A"
                ),
                "created_ts": (
                    user.created_ts.strftime(rf"%B %d %Y") if user.created_ts else "N/A"
                ),
            }
            for user in all_users
        ]

        return {
            "message": constants.ALL_USERS_RETRIEVED,
            "success": True,
            "data": users_data,
        }
    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def get_specific_user_details(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }
        specific_user_details = (
            db.query(
                User.first_name,
                User.last_name,
                User.phone,
                User.email,
                User.image,
                User.is_active,
                User.last_login,
                User.created_ts,
            )
            .filter(User.id == user.id)
            .first()
        )

        gender = db.query(UserDetails).filter(UserDetails.user_id == user.id).first()

        total_questions_answered = (
            db.query(func.count(Questions.id))
            .filter(Questions.user_id == user_id, Questions.is_answered == True)
            .scalar()
        )

        total_journal_count = (
            db.query(Journal).filter(Journal.user_id == user_id).count()
        )

        total_days = (datetime.now() - user.created_ts).days

        average_number_of_questions_per_day = total_questions_answered / total_days
        average_number_of_questions_per_day = round(
            average_number_of_questions_per_day, 2
        )

        return {
            "message": "Specific User Details",
            "success": True,
            "data": {
                "full_name": f"{specific_user_details.first_name} {specific_user_details.last_name}",
                "phone": (
                    specific_user_details.phone
                    if specific_user_details.phone
                    else "N/A"
                ),
                "email": (
                    specific_user_details.email
                    if specific_user_details.email
                    else "N/A"
                ),
                "image": specific_user_details.image,
                "is_active": specific_user_details.is_active,
                "last_login": (
                    format_datetime_custom(specific_user_details.last_login)
                    if specific_user_details.last_login
                    else "N/A"
                ),
                "created_ts": (
                    specific_user_details.created_ts.strftime(rf"%B %d %Y")
                    if specific_user_details.created_ts
                    else "N/A"
                ),
                "gender": gender if gender else "Not-specified",
                "average_number_of_questions_per_day": average_number_of_questions_per_day,
                "total_questions_answered": total_questions_answered,
                "total_journal_count": total_journal_count,
            },
        }

    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def update_user_status(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            return {
                "message": constants.USER_NOT_FOUND,
                "success": False,
            }
        user.is_active = not user.is_active

    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def get_user_profile_graph_details(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return {"message": constants.USER_NOT_FOUND, "success": False}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        journals = (
            db.query(Journal.id, func.date(Journal.created_ts).label("created_date"))
            .filter(Journal.user_id == int(user_id))
            .filter(Journal.created_ts.between(start_date, end_date))
            .subquery()
        )

        # Main query to count journals per day
        jounral_results = (
            db.query(journals.c.created_date, func.count(journals.c.id).label("count"))
            .group_by(journals.c.created_date)
            .order_by(journals.c.created_date)
            .all()
        )

        question = (
            db.query(
                Questions.id, func.date(Questions.updated_ts).label("answered_date")
            )
            .filter(Questions.updated_ts.between(start_date, end_date))
            .filter(Questions.user_id == int(user_id))
            .filter(Questions.updated_ts != Questions.created_ts)
            .subquery()
        )
        question_result = (
            db.query(question.c.answered_date, func.count(question.c.id).label("count"))
            .group_by(question.c.answered_date)
            .order_by(question.c.answered_date)
            .all()
        )

        end_date = int(datetime.now().strftime(rf"%d"))
        start_date = int((datetime.now() - timedelta(days=7)).strftime(rf"%d")) + 1

        journal_data = [
            {"date": int(result.created_date.strftime(rf"%d")), "count": result.count}
            for result in jounral_results
        ]
        question_data = [
            {"date": int(result.answered_date.strftime(rf"%d")), "count": result.count}
            for result in question_result
        ]

        new_journal_data = []
        for i in range(start_date, end_date + 1):
            found = False
            for result in journal_data:
                if i == result["date"]:
                    new_journal_data.append(result["count"])
                    found = True
                    break
            if not found:
                new_journal_data.append(0)

        new_question_data = []
        for i in range(start_date, end_date + 1):
            found = False
            for result in question_data:
                if i == result["date"]:
                    new_question_data.append(result["count"])
                    found = True
                    break
            if not found:
                new_question_data.append(0)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)

        date_arr = [
            (start_date + timedelta(days=i)).strftime(rf"%m/%d/%Y")
            for i in range((end_date - start_date).days + 1)
        ]
        return {
            "success": True,
            "message": "Success",
            "data": {
                "date_arr": date_arr,
                "logins_per_day_of_week": [1, 9, 19, 0, 1, 1, 0],
                "journal_entries_per_day_of_week": new_journal_data,
                "question_answered_per_day_of_week": new_question_data,
                "engagement_score_per_day_of_week": [14, 9, 1, 0, 11, 11, 0],
            },
        }
    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}


async def update_detail_of_user(
    request: UpdateUserDetails, db: Session, current_user: CurrentUser
):
    try:
        user = db.query(User).filter(User.id == current_user["id"]).first()

        user_details = (
            db.query(UserDetails)
            .filter(UserDetails.user_id == current_user["id"])
            .first()
        )

        if not user_details:
            user_details = UserDetails(
                user_id=current_user["id"],
                address=request.address,
                dob=request.dob,
                field_of_study=request.field_of_study,
                gender=request.gender,
            )
            db.add(user_details)
            db.flush()
            db.commit()
        else:
            user_details.field_of_study = request.field_of_study
            user_details.address = request.address
            user_details.dob = request.dob
            user_details.gender = request.gender

            db.commit()
        # user.country_code = request.country_code
        current_user["first_name"] = request.first_name
        current_user["last_name"] = request.last_name
        current_user["phone"] = request.phone
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.phone = request.phone
        db.commit()

        return {
            "message": constants.USER_UPDATED_SUCCESSFULLY,
            "success": True,
            "data": request,
        }

    except Exception as e:
        print(e)
        return {"message": constants.SOMETHING_WENT_WRONG, "success": False}

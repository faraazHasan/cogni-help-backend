from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel  # type: ignore


class EducationSchema(BaseModel):
    id: Optional[int] = None
    field_of_study: Optional[str] = None
    level_of_education: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    appearing: Optional[bool] = None


class WorkHistorySchema(BaseModel):
    id: Optional[int] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    still_working_here: Optional[bool] = None


class finalData(BaseModel):
    field_id: Optional[int] = None
    value: Optional[str | bool | List[str] | int] = None
    field_name: Optional[str] = None
    form_group_id: Optional[int] = None
    inner_group_id: Optional[int] = None
    is_enabled: Optional[bool] = None


class UserDetailsSchema(BaseModel):
    profile_summary: List[finalData] = None
    update_index: Optional[int] = 1


class EducationAndWorkHistorySchema(BaseModel):
    education: List[EducationSchema]
    work_history: List[WorkHistorySchema]
    deletedEducation: List[int]
    deletedWork: List[int]


class FamilyDetails(BaseModel):
    id: Optional[int] = None
    relationship: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    email: Optional[str] = None
    special_notes: Optional[str] = None


class FamilyDetailsSchema(BaseModel):
    member: List[FamilyDetails]
    deletedMembers: List[int]


class PersonalPreferencesSchema(BaseModel):
    favourite_foods: Optional[List[str]] = None
    favourite_places: Optional[List[str]] = None
    favourite_movies: Optional[List[str]] = None
    favourite_music: Optional[List[str]] = None
    favourite_books: Optional[List[str]] = None
    hobbies_and_interests: Optional[List[str]] = None
    special_notes: Optional[str] = None


from typing import Optional

from pydantic import BaseModel, Field


class UserProfileSchema(BaseModel):
    first_name: str
    last_name: str
    gender: str
    image: Optional[str] = ""
    address: str
    dob: str
    phone: str
    # phone: str
    # # country_code: str


class CurrentUser(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    account_type: str
    company_id: int
    phone: str
    image: str
    email: str
    account_type: str
    password: str
    is_active: bool
    is_verified: bool
    verification_code: str
    last_login: str
    country_code: str
    created_ts: str
    updated_ts: str


class FileType(str, Enum):
    document = "documents"
    image = "images"
    training_document = "training-documents"


class PresignedUrlRequest(BaseModel):
    file_path: str = Field(
        ..., description="List of filenames to generate presigned URLs for."
    )
    file_format: str = Field(
        ..., description="The type of files to upload, either 'document' or 'image'."
    )


class ProfileImageSchema(BaseModel):
    url: str = Field(
        ..., description="List of filenames to generate presigned URLs for."
    )


class UpdatePasswordSchema(BaseModel):
    password: str
    new_password: str


class AccountDeleteSchema(BaseModel):
    user_id: Optional[int] = None


class SetQuestionsCountSchema(BaseModel):
    count: Optional[int] = None


class UpdateUserDetails(BaseModel):
    first_name: Optional[str] | None
    last_name: Optional[str] | None
    phone: Optional[str] | None
    gender: Optional[str] | None
    dob: Optional[str] | None
    address: Optional[str] | None
    field_of_study: Optional[str] | None
    # country_code : Optional[str] | None

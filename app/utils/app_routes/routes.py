from pydantic import BaseModel


class Routes:
    AUTH = "/auth"
    SIGNUP = "/signup"
    VERIFY = "/otp-verification"
    RESET_PASSWORD = "/reset-password"
    FORGOT_PASSWORD = "/forgot-password"
    LOGIN = "/login"
    RESEND_VERIFICATION_CODE = "/resend-verification-code"
    PROFILE_UPDATE = "/profile_update"
    GET_PRE_SIGN_URL = "/pre-signed-url"
    GET_DAILY_QUESTIONS = "/daily-questions"
    UPDATE_QUESTION_STATUS = "/update-question-status"
    UPLOAD_PROFILE_IMAGE = "/upload-profile-image"
    UPDATE_PASSWORD = "/update-password"
    ACCOUNT_DELETE = "/account-delete"
    GET_DASHBOARD_DETAILS = "/get-dashboard-details"
    GET_ALL_USERS = "/get-all-users"
    GENERATE_QUESTIONS = "/generate-questions"
    GENERATE_QUESTIONS_USING_JOURNAL = "/generate-questions-journal"
    SET_QUESTIONS_COUNT = "/set-questions-count"
    GET_SPECIFIC_USER_DETAIL = "/get-specific-user-details"
    UPDATE_USER_STATUS = "/update-user-status"
    GET_USER_GRAPH_DETAILS = "/get-user-graph-details"
    UPDATE_USER_DETAILS = "/update-user-details"


# Define the TypedDicts
class Auth(BaseModel):
    INDEX: str
    SIGNUP: str
    VERIFY: str
    RESET_PASSWORD: str
    FORGOT_PASSWORD: str
    LOGIN: str
    UPDATE_ADMIN_IMAGE: str
    UPDATE_ADMIN_DETAILS: str
    UPDATE_PASSWORD: str


class User(BaseModel):
    INDEX: str
    ADD_USER_DETAILS: str
    GET_USER_DETAILS: str
    EDUCATION_AND_WORK_HISTORY: str
    FAMILY_DETAILS: str
    PERSONAL_PREFERENCES: str
    GET_DASHBOARD_DETAILS: str
    GET_ALL_USERS: str
    UPDATE_USER_DETAILS: str
    GET_FORM_VALUES: str


class FormBuilder(BaseModel):
    INDEX: str
    CREATE: str
    UPDATE: str
    GET_ALL: str
    GET_FORM_COUNT: str


class Questions(BaseModel):
    INDEX: str
    GET_DAILY_QUESTIONS: str
    SUBMIT_ANSWER: str
    REDUCE_OPTIONS: str
    SKIP_QUESTION: str
    CHANGE_CURRENT_QUESTION_ID: str


class AppRoutes(BaseModel):
    auth: Auth
    user: User
    form_builder: FormBuilder
    questions: Questions


# Create instances of Auth and User as dictionaries
auth_routes: Auth = {
    "INDEX": "/auth",
    "SIGNUP": "/signup",
    "VERIFY": "/otp-verification",
    "RESET_PASSWORD": "/reset-password",
    "FORGOT_PASSWORD": "/forgot-password",
    "LOGIN": "/login",
    "UPDATE_ADMIN_IMAGE": "/update-admin-image",
    "UPDATE_ADMIN_DETAILS": "/update-admin-details",
    "UPDATE_PASSWORD": "/update-password",
}

user_routes: User = {
    "INDEX": "/user",
    "ADD_USER_DETAILS": "/add-user-details",
    "GET_USER_DETAILS": "/get-user-details",
    "EDUCATION_AND_WORK_HISTORY": "/education-and-work-history",
    "FAMILY_DETAILS": "/family-details",
    "PERSONAL_PREFERENCES": "/personal-preferences",
    "GET_DASHBOARD_DETAILS": "/get-dashboard-details",
    "GET_ALL_USERS": "/get-all-users",
    "UPDATE_USER_DETAILS": "/update-user-details",
    "GET_FORM_VALUES": "/get-form-values",
}

form_builder_routes: FormBuilder = {
    "INDEX": "/form-builder",
    "CREATE": "/create-form",
    "UPDATE": "/update-form",
    "GET_ALL": "/get-forms",
    "GET_FORM_COUNT": "/get-form-count",
}

questions_routes: Questions = {
    "INDEX": "/questions",
    "GET_DAILY_QUESTIONS": "/daily-questions",
    "SUBMIT_ANSWER": "/submit-answer",
    "REDUCE_OPTIONS": "/reduce-options",
    "SKIP_QUESTION": "/skip-question",
    "CHANGE_CURRENT_QUESTION_ID": "/change-current-question-id",
}

# Create an instance of AppRoutes
app_routes = AppRoutes(
    auth=auth_routes,
    user=user_routes,
    form_builder=form_builder_routes,
    questions=questions_routes,
)

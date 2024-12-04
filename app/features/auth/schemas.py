from pydantic import BaseModel, EmailStr

# from app.utils.constants import phone_regex, password_regex

password_regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,16}$"
phone_regex = r"^\+1\d{10}$"


class UserSchema(BaseModel):
    first_name: str
    last_name:str
    email: EmailStr
    password: str


class VerifyUserSignupOtpSchema(BaseModel):
    otp: int
    email: str


class ResetPasswordFormSchema(BaseModel):
    email: str
    password: str


class ForgotPassSchema(BaseModel):
    email: EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    account_type: str


class ResendVerificationCodeSchema(BaseModel):
    email: EmailStr
    type: str


class UpdateAdminImage(BaseModel):
    email:EmailStr
    image: str
    
    
class UpdatePassword(BaseModel):
    email: EmailStr
    new_password:str
    confirm_password:str
    
class UpdateAdminDetails(BaseModel):
    email: EmailStr
    first_name:str
    last_name:str
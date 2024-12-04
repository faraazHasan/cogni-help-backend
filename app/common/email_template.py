from email_sendgrid_utils import send_email

from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()


def send_verify_otp_email(user_email, otp, mailType):
    subject = ""
    if mailType == "forgotPassword":
        subject = "Password Reset OTP Code"
    else:
        subject = "Sign up otp"
    send_email(keys["SENDER_EMAIL"], user_email, subject, f"Your OTP code is - {otp}")

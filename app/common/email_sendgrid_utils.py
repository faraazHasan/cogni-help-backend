import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To

from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()

sg = sendgrid.SendGridAPIClient(api_key=keys["SENGRID_API_KEY"])


def send_email(from_email, to_email, subject, content):
    try:
        from_email = Email(keys["SENDER_EMAIL"])
        to_email = To(to_email)
        subject = subject
        content = Content("text/html", content)
        mail = Mail(from_email, to_email, subject, content)
        mail_json = mail.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        return response.status_code
    except:
        return {
            "message": "Could not send mail",
            "success": False,
        }

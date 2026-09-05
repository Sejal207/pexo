from fastapi_mail import ConnectionConfig
from pydantic import EmailStr

mail_config = ConnectionConfig(
    MAIL_USERNAME="test",
    MAIL_PASSWORD="password",
    MAIL_FROM=EmailStr("noreply@Pexo.internal"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.mailtrap.io",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

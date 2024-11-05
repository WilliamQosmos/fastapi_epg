import logging

from fastapi_mail import FastMail, MessageSchema, MessageType

from app.core.config import settings


class EmailService:
    def __init__(self) -> None:
        self.fast_mail = FastMail(settings.email_config)

    async def send_email(
        self,
        email_to: str | list[str],
        subject: str = "",
        html_content: str = "",
    ) -> None:
        assert settings.emails_enabled, "no provided configuration for email variables"
        message = MessageSchema(
            subject=subject,
            recipients=[email_to] if not isinstance(email_to, list) else email_to,
            body=html_content,
            subtype=MessageType.html,
        )
        response = await self.fast_mail.send_message(message)
        logging.info(f"send email result: {response}")

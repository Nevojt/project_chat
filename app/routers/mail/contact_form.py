
from fastapi import APIRouter, HTTPException
from app.mail.send_mail import send_mail_for_contact_form
from app.schemas import mail

router = APIRouter(
    prefix="/contact-form",
    tags=["contact"],
    responses={404: {"description": "Not found"}},
)

@router.post("/send-email/")
async def send_email(contact: mail.ContactForm):
    try:
        await send_mail_for_contact_form(contact)
        return {"status": "Email sent successfully to support team"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
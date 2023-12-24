from passlib.context import CryptContext
import secrets
import hashlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def generate_unique_token(email: str) -> str:
    # Create a base token using a new random number
    base_token = secrets.token_urlsafe()
    # Use the user's email to personalize the token
    personalized_token = f"{base_token}{email}"
    # Create a SHA256 hash of the personalized token
    return hashlib.sha256(personalized_token.encode()).hexdigest()
import uuid
from passlib.context import CryptContext
import secrets
import hashlib
import string, random
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    """
    Hash a password using the CryptContext from passlib.context.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    """
    Verify that a plaintext password matches a previously hashed password.

    Args:
        plain_password (str): The plaintext password to compare.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_unique_token(email: str) -> str:
    """
    Generate a unique and secure token for a user.

    Args:
        email (str): The email of the user for which to generate the token.

    Returns:
        str: A unique and secure token for the user.
    """
    # Create a base token using a new random number
    base_token = secrets.token_urlsafe()
    # Use the user's email to personalize the token
    personalized_token = f"{base_token}{email}"
    # Create a SHA256 hash of the personalized token
    return hashlib.sha256(personalized_token.encode()).hexdigest()



def generate_reset_code():
    return ''.join(random.choices(string.digits, k=6))


def generate_random_code(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_access_code():
    return str(uuid.uuid4())
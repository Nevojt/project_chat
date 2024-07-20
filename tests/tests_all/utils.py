import random
import string



def random_lower_string() -> str:
    """
    Generate a random lowercase string of length 32.

    This function uses the `random.choices` method from the `random` module to generate a random lowercase string.
    The `string.ascii_lowercase` constant is used as the input characters for the `random.choices` method.
    The generated string has a length of 32 characters.

    Parameters:
    None

    Returns:
    str: A random lowercase string of length 32.
    """
    return "".join(random.choices(string.ascii_lowercase, k=15))


def random_email() -> str:
    """
    Generate a random email address.

    The function generates a random email address using the `random_lower_string` function.
    The email address consists of a random lowercase string followed by '@', another random lowercase string,
    and '.testuser'.

    Parameters:
    None

    Returns:
    str: A random email address in the format "random_string@random_string.testuser"
    """
    return f"{random_lower_string()}@{random_lower_string()}.testuser"

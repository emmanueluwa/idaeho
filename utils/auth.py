from passlib.context import CryptContext

pwd_context = CryptContext(schemas=["bcrypt"], deprecated="auto")


def hash_passowrd(password: str) -> str:
    """
    args:
        plain text password

    returns:
        hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    args:
        plain password
        hashed password

    returns:
        true / false depending on password match
    """
    return pwd_context.verify(plain_password, hashed_password)

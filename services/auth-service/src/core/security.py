from datetime import datetime, timezone, timedelta

import jwt
from src.core.config import settings
from src.core.ad_client import verify_login
from src.logger import logger


def new_token(username: str, password: str) -> str:
    """create a new JWT using username and password

    Args:
        username (str): username of AD user (only username, no special domain formatting)
        password (str): plain text password of user username

    Returns:
        str: credible input, returns new token
    """
    logger.info(username)
    ad_username = verify_login(username.strip(), password)
    payload = {
        "username": ad_username,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    return token

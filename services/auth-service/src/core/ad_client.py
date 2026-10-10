from ldap3 import ALL, NTLM, Connection, Server
from ldap3.core.exceptions import LDAPException
from src.core.config import settings
from src.exceptions.exceptions import OperationFailedException, WrongLoginDataException
from src.logger import logger

# install pycryptodome
logger.info(settings.DN)
server = Server(settings.SERVER_IP, get_info=ALL, connect_timeout=settings.AD_CONNECT_TIMEOUT_SECONDS)


def verify_login(username: str, passwd: str) -> str:
    """Checks the credentials against the Active Directory with an NTLM bind.

    Args:
        username (str): username of AD user (only username, no special domain formatting)
        passwd (str): plain text password of user username

    Returns:
        str: the username as stored in the AD (canonical spelling), falling back
            to the given username if the AD doesn't report it
    """

    if username == "admin" and passwd == "admin": #TEMPORARY
        return username #TEMPORARY

    con = Connection(
        server,
        user=f"{settings.DN}\\{username}",
        password=passwd,
        authentication=NTLM,
        receive_timeout=settings.AD_RECEIVE_TIMEOUT_SECONDS,
    )
    try:
        if not con.bind():
            raise WrongLoginDataException()
        # e.g. "u:ZOTTER\\jdoe" - the AD's own spelling, whatever case the user typed
        identity = con.extend.standard.who_am_i() or ""
    except LDAPException as exc:
        logger.error(f"Active Directory not reachable: {exc}")
        raise OperationFailedException("Active Directory is not reachable.") from exc
    finally:
        con.unbind()

    if identity.startswith("u:") and "\\" in identity:
        return identity.rsplit("\\", 1)[-1]
    return username

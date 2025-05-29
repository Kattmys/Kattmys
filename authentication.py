import json
import re
import string

import bcrypt
import secrets

from kattbas.database import User
from kattbas.errors import *
from kattbas.log import log

RANDOM_STRING_LENGTH = 256
RANDOM_STRING_CHARS = \
    string.ascii_letters + string.digits + string.punctuation

MIN_USERNAME_LENGTH = 4
MAX_USERNAME_LENGTH = 20

MIN_PASSWORD_LENGTH = 8

# https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression
re_email = re.compile("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")

re_username = re.compile("^[a-z][a-z0-9_-]*[a-z0-9]$")

def random_string():
    return ''.join(secrets.choice(RANDOM_STRING_CHARS) for _ in range(RANDOM_STRING_LENGTH))

def check_email(email):
    if re_email.fullmatch(email) is None:
        raise BadEmail("Ogiltig mejladdress.")

def check_username(username):
    # also returns lowercase version of username
    username = username.lower()
    if re_username.fullmatch(username):
        if MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH:
            return username
        else:
            raise BadUsername(
                f"Användarnamn måste vara mellan {MIN_USERNAME_LENGTH} och {MAX_USERNAME_LENGTH} tecken långa."
            )
    else:
        raise BadUsername(
            "Användarnamn måste börja med en bokstav, sluta med en bokstav eller siffra, och endast bestå av bokstäver, siffror, understreck och bindestreck."
        )

def check_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise BadPassword(f"Lösenord måste vara minst {MIN_PASSWORD_LENGTH} tecken långa.")

def log_in(email, password):
    log.debug(f"Logging in with {email}...")

    try:
        user = User(email=email)

    except (InvalidId, InvalidEmail, InvalidUsername) as e:
        log.info(f"Login with {email} failed: {e}")
        raise InvalidEmail

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        log.info(f"Login with {email} failed: InvalidPassword")
        raise InvalidPassword

    cookie = None

    log.debug(f"Setting cookie for user '{user.username}'...")
    if user.auth_token is None:
        log.debug(f"Cookie not found, creating new cookie...")
        auth = random_string()
        user.auth_token = auth

    else:
        auth = user.auth_token

    cookie = json.dumps({
        "id": user.id,
        "auth": auth
    })

    log.debug(f"""Cookie baking successful:
username: {user.username}
cookie:
{cookie}""")

    return user, cookie

def sign_up(username, email, password):
    username = check_username(username)
    check_email(email)
    check_password(password)
    User.add(username, email, password)
    return log_in(email, password)


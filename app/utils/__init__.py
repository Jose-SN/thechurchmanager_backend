import secrets
import bcrypt
from typing import Optional

def generate_otp(otp: str = '') -> str:
    if len(otp) == 5:
        return otp
    random_i = str(secrets.randbelow(10))
    if random_i not in otp and not (not otp and random_i == '0'):
        otp += random_i
    return generate_otp(otp)

async def get_hashed_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

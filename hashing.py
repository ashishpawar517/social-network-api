# hashing
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def encrypt(password: str):
        return pwd_context.hash(password)

    def verify(hashed_password, plain_passoword):
        return pwd_context.verify(plain_passoword, hashed_password)

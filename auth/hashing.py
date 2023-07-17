from passlib.context import CryptContext


pwd_cxt = CryptContext(schemes=["bcrypt"])

# Class to Encypt and Decrypt the password - for user registration and user login
class Hash:
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    def verify(hashed_password, password):
        return pwd_cxt.verify(password, hashed_password)

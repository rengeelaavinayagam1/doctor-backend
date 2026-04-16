import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Password-ah sha256 panni apram bcrypt panna length issue varadhu
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(pwd_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(pwd_hash, hashed_password)
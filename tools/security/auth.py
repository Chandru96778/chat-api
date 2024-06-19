from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
#from jose import JWTError, jwt
from models.usermodel import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# async def check_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = db.query(models.User).filter(models.User.username == token_data.username).first()
#     if user is None:
#         raise credentials_exception
#     return user

def check_user():

    return 'default_user@trcsolutions.com'

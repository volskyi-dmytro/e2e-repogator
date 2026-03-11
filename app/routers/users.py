from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, TokenResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # WARNING: storing password in plain text — no hashing
    # TODO: use bcrypt: hashed = bcrypt.hashpw(user_in.password.encode(), bcrypt.gensalt())
    # TODO: hash this password
    user = User(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,  # plain text — insecure
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Plain text comparison — should be bcrypt.checkpw()
    if user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Returning a trivially forgeable token — should be JWT
    token = f"user_id:{user.id}"
    return TokenResponse(token=token, user_id=user.id)

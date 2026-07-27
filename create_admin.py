from database import SessionLocal
from models import UserModel
from security import hash_password
from dotenv import load_dotenv
import os

load_dotenv()
def create_admin():
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not email or not password:
        raise RuntimeError(
            "Admin credentials are missing from the .env file"
        )

    db = SessionLocal()

    try:
        existing_admin = (
            db.query(UserModel)
            .filter(
                (UserModel.username == username)
                | (UserModel.email == email)
            )
            .first()
        )

        if existing_admin is not None:
            print("Admin already exists.")
            return

        admin = UserModel(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role="admin"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
from database import SessionLocal
from models import UserModel
from security import hash_password


def create_admin():
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(UserModel)
            .filter(UserModel.username == "admin")
            .first()
        )

        if existing_admin is not None:
            print("Admin already exists.")
            return

        admin = UserModel(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin12345"),
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace 'your_password' with your actual PostgreSQL password
DATABASE_URL = "postgresql://postgres:cherry123@localhost:5432/autosocial"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from app.core.config import get_settings
from sqlalchemy.orm import sessionmaker

settings = get_settings()

# ENV Variables
DATABASE_URL = settings.DATABASE_URL

# Create Engine
engine = create_engine(DATABASE_URL)

# Create Session
Session = sessionmaker(
    bind=engine,
    autoflush=False,
)


# Function: Get DB Object
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()


engine = create_engine(keys["DATABASE_URI"], pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def db_connection():
    db = SessionLocal()
    try:
        print("Opening db connection", db)
        db.begin()
        yield db
        db.commit()
    except Exception as e:
        print("Error in db_connection", e)
        db.rollback()
        raise
    finally:
        print("Closing db connection")
        db.close()

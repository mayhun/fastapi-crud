from .database import engine
from . import models

def create_tables():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()

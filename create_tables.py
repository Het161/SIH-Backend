"""
Script to create all database tables
Run this once before starting your FastAPI server
"""
from app.db.session import engine, Base
from app.db.models.user import User
from app.db.models.task import Task

def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    
    # This creates all tables defined in your models
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("Tables created: users, tasks")

if __name__ == "__main__":
    create_tables()

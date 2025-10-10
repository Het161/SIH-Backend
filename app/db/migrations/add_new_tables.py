"""
Database migration script for new features:
- api_access_logs
- automation_rules
"""

from sqlalchemy import create_engine
from app.db.session import Base
from app.core.config import settings

# Import all models to register them
from app.db.models.access_log import APIAccessLog
from app.db.models.automation_rule import AutomationRule
from app.db.models.task import Task
from app.db.models.audit_log import AuditLog

def run_migration():
    """Create all new tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Migration complete!")

if __name__ == "__main__":
    run_migration()

import logging
from app.db.session import Session
from app.db.models.role import Role

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_roles():
    db = Session()
    try:
        roles_to_seed = ["admin", "manager", "employee", "employe"]
        for role_name in roles_to_seed:
            existing_role = db.query(Role).filter(Role.role_name == role_name).first()
            if not existing_role:
                new_role = Role(role_name=role_name)
                db.add(new_role)
                logger.info(f"Adding role: {role_name}")
            else:
                logger.info(f"Role already exists: {role_name}")
        db.commit()
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()

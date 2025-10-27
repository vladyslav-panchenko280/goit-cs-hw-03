"""Seed data script to replace seed.py"""
from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Status, Task
import random

fake = Faker()


def seed_users(db: Session, count: int = 10):
    """Generate and insert random users"""
    print(f"Seeding {count} users...")
    users = []
    for _ in range(count):
        user = User(
            username=fake.user_name(),
            email=fake.email()
        )
        users.append(user)
    
    db.bulk_save_objects(users)
    db.commit()
    print(f"{count} users seeded")


def seed_tasks(db: Session, count: int = 30):
    """Generate and insert random tasks"""
    print(f"Seeding {count} tasks...")
    
    users = db.query(User).all()
    statuses = db.query(Status).all()
    
    if not users:
        print("No users found. Please seed users first.")
        return
    
    if not statuses:
        print("No statuses found. Migration may not have run.")
        return
    
    tasks = []
    for _ in range(count):
        task = Task(
            title=fake.sentence(nb_words=4).rstrip('.'),
            description=fake.text(max_nb_chars=200),
            status_id=random.choice(statuses).id,
            user_id=random.choice(users).id
        )
        tasks.append(task)
    
    db.bulk_save_objects(tasks)
    db.commit()
    print(f"{count} tasks seeded")


def main():
    """Main function to seed database"""
    print("Starting database seeding...")
    
    db = SessionLocal()
    try:
        seed_users(db, count=10)
        seed_tasks(db, count=30)
        
        user_count = db.query(User).count()
        status_count = db.query(Status).count()
        task_count = db.query(Task).count()
        
        print("Database seeding completed!")
        print(f"Total users: {user_count}")
        print(f"Total statuses: {status_count}")
        print(f"Total tasks: {task_count}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


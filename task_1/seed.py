from faker import Faker
from utils import get_db_connection, safe_execute

fake = Faker()


def seed_users(cursor, count=10):
    """Generate and insert random users"""
    print(f"Inserting {count} users...")
    for _ in range(count):
        username = fake.user_name()
        email = fake.email()
        safe_execute(
            cursor,
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (username, email),
            f"Failed to insert user {username}"
        )
    print(f"{count} users inserted")


def seed_statuses(cursor):
    """Insert task statuses"""
    statuses = ['new', 'in progress', 'completed']
    print(f"Inserting {len(statuses)} statuses...")
    for status in statuses:
        safe_execute(
            cursor,
            "INSERT INTO status (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
            (status,),
            f"Failed to insert status {status}"
        )
    print(f"{len(statuses)} statuses inserted")


def seed_tasks(cursor, count=30):
    """Generate and insert random tasks"""
    print(f"Inserting {count} tasks...")
    
    if not safe_execute(cursor, "SELECT id FROM users", error_message="Failed to select users"):
        return
    user_ids = [row[0] for row in cursor.fetchall()]
    
    if not safe_execute(cursor, "SELECT id FROM status", error_message="Failed to select statuses"):
        return
    status_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(count):
        title = fake.sentence(nb_words=4).rstrip('.')
        description = fake.text(max_nb_chars=200)
        status_id = fake.random_element(status_ids)
        user_id = fake.random_element(user_ids)
        safe_execute(
            cursor,
            "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s)",
            (title, description, status_id, user_id),
            "Failed to insert task"
        )
    print(f"{count} tasks inserted")


def main():
    """Main function to seed database"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        seed_users(cursor, count=10)
        seed_statuses(cursor)
        seed_tasks(cursor, count=30)
        
        connection.commit()
        print("\nDatabase seeded successfully!")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"\nTotal users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM status")
        print(f"Total statuses: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        print(f"Total tasks: {cursor.fetchone()[0]}")
        
    except Exception as e:
        connection.rollback()
        print(f"\nError seeding database: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()


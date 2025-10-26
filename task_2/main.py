import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()


class CatDatabase:
    """MongoDB CRUD operations for cat collection"""
    
    def __init__(self):
        """Initialize MongoDB connection using environment variables"""
        mongo_host = os.getenv('MONGO_HOST', 'localhost')
        mongo_port = os.getenv('MONGO_PORT', '27017')
        mongo_username = os.getenv('MONGO_USERNAME', 'admin')
        mongo_password = os.getenv('MONGO_PASSWORD', 'password')
        mongo_db = os.getenv('MONGO_DB', 'cats_db')
        mongo_collection = os.getenv('MONGO_COLLECTION', 'cats')
        
        connection_string = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/"
        
        self.client = MongoClient(connection_string, server_api=ServerApi('1'))
        self.db = self.client[mongo_db]
        self.collection = self.db[mongo_collection]
        
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
    
    def read_all(self):
        """Read and display all cats from the collection"""
        cats = list(self.collection.find())
        
        if not cats:
            print("\nNo cats found in the database.")
            return
        
        print(f"Found {len(cats)} cat(s) in the database:")
        
        for cat in cats:
            self._print_cat(cat)
    
    def read_by_name(self, name):
        """Find and display cat by name"""
        cat = self.collection.find_one({"name": name})
        
        if cat:
            print(f"Found cat: {name}")
            self._print_cat(cat)
        else:
            print(f"\n✗ Cat with name '{name}' not found.")
    
    def update_age(self, name, new_age):
        """Update cat's age by name"""
        try:
            new_age = int(new_age)
            if new_age < 0:
                print("\n✗ Age must be a positive number.")
                return
            
            result = self.collection.update_one(
                {"name": name},
                {"$set": {"age": new_age}}
            )
            
            if result.matched_count > 0:
                print(f"\nSuccessfully updated age for '{name}' to {new_age}")
            else:
                print(f"\nCat with name '{name}' not found.")
        except ValueError:
            print("\nInvalid age. Please enter a number.")
    
    def add_feature(self, name, feature):
        """Add a new feature to cat's features list"""
        result = self.collection.update_one(
            {"name": name},
            {"$push": {"features": feature}}
        )
        
        if result.matched_count > 0:
            print(f"\nSuccessfully added feature '{feature}' to '{name}'")
        else:
            print(f"\nCat with name '{name}' not found.")
    
    def delete_by_name(self, name):
        """Delete cat by name"""
        result = self.collection.delete_one({"name": name})
        
        if result.deleted_count > 0:
            print(f"\nSuccessfully deleted cat '{name}'")
        else:
            print(f"\nCat with name '{name}' not found.")
    
    def delete_all(self):
        """Delete all cats from the collection"""
        result = self.collection.delete_many({})
        print(f"\nSuccessfully deleted {result.deleted_count} cat(s) from the database.")
    
    def create_cat(self, name, age, features):
        """Create a new cat (helper method for testing)"""
        cat = {
            "name": name,
            "age": age,
            "features": features
        }
        result = self.collection.insert_one(cat)
        print(f"\nSuccessfully created cat '{name}' with ID: {result.inserted_id}")
        return result.inserted_id
    
    def _print_cat(self, cat):
        """Helper method to print cat information"""
        print(f"\nID: {cat['_id']}")
        print(f"Name: {cat['name']}")
        print(f"Age: {cat['age']}")
        print(f"Features: {', '.join(cat['features'])}")
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("\nDatabase connection closed.")


def display_menu():
    """Display the main menu"""
    print("CAT DATABASE - CRUD OPERATIONS")
    print("1. Show all cats")
    print("2. Find cat by name")
    print("3. Update cat's age")
    print("4. Add feature to cat")
    print("5. Delete cat by name")
    print("6. Delete all cats")
    print("7. Add a new cat (for testing)")
    print("0. Exit")


def main():
    """Main function to run the CRUD application"""
    db = CatDatabase()
    
    if db.collection.count_documents({}) == 0:
        print("\nDatabase is empty. Adding sample data...")
        db.create_cat("barsik", 3, ["ходить в капці", "дає себе гладити", "рудий"])
        db.create_cat("murka", 2, ["любить молоко", "сіра", "грається з м'ячиком"])
        db.create_cat("snow", 5, ["біла", "пухнаста", "любить спати"])
    
    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            db.read_all()
        
        elif choice == "2":
            name = input("Enter cat's name: ").strip()
            if name:
                db.read_by_name(name)
            else:
                print("\nName cannot be empty.")
        
        elif choice == "3":
            name = input("Enter cat's name: ").strip()
            age = input("Enter new age: ").strip()
            if name and age:
                db.update_age(name, age)
            else:
                print("\nName and age cannot be empty.")
        
        elif choice == "4":
            name = input("Enter cat's name: ").strip()
            feature = input("Enter new feature: ").strip()
            if name and feature:
                db.add_feature(name, feature)
            else:
                print("\nName and feature cannot be empty.")
        
        elif choice == "5":
            name = input("Enter cat's name to delete: ").strip()
            if name:
                confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ").strip().lower()
                if confirm == "yes":
                    db.delete_by_name(name)
                else:
                    print("\nDeletion cancelled.")
            else:
                print("\nName cannot be empty.")
        
        elif choice == "6":
            confirm = input("Are you sure you want to delete ALL cats? (yes/no): ").strip().lower()
            if confirm == "yes":
                db.delete_all()
            else:
                print("\nDeletion cancelled.")
        
        elif choice == "7":
            name = input("Enter cat's name: ").strip()
            age = input("Enter cat's age: ").strip()
            features_input = input("Enter features (comma-separated): ").strip()
            
            if name and age and features_input:
                try:
                    age = int(age)
                    features = [f.strip() for f in features_input.split(",")]
                    db.create_cat(name, age, features)
                except ValueError:
                    print("\nInvalid age. Please enter a number.")
            else:
                print("\nAll fields are required.")
        
        elif choice == "0":
            print("\nExiting...")
            db.close()
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()


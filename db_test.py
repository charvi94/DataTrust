from services.database import initialize_database, DATABASE_PATH


initialize_database()

print("Database initialized successfully.")
print("Database location:")
print(DATABASE_PATH)
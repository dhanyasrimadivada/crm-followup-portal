from db import seed_db

if __name__ == "__main__":
    seed_db(force=True)
    print("Demo CRM database reset successfully.")
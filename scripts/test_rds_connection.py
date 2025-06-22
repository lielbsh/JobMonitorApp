from sqlalchemy import create_engine, text
from settings import DATABASE_URL

engine = create_engine(DATABASE_URL)

def test_connection():
    print("🔌 Testing connection to RDS...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"✅ Success! Result: {result.scalar()}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()

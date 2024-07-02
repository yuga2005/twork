import random
import string
from datetime import datetime
import sqlite3
import redis
from functools import wraps

# Redis connection details
redis_host = "localhost"
redis_port = 6379

MAX_RETRIES = 3

# Database connection details
db_file = "tracking_numbers.db"

def create_new_connection():
  """
  Creates a connection to the SQLite database and ensures the 'tracking_numbers' table exists.
  """
  conn = None
  try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracking_numbers'")
    if cursor.fetchone() is None:
      # Create the table if it doesn't exist
      cursor.execute('''CREATE TABLE tracking_numbers (
                          tracking_number TEXT PRIMARY KEY
                       )''')
      conn.commit()

  except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
  finally:
    if conn:
      cursor.close()
  return conn

def create_connection():
  """
  Creates a connection to the SQLite database.
  """
  conn = None
  try:
    conn = sqlite3.connect(db_file)
  except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
  return conn

def generate_tracking_number(prefix="", length=10):
  """
  Generates a unique tracking number with a prefix and specified length.
  """
  timestamp = datetime.now().strftime("%y%m%d%H%M%S%f")[:-3]
  random_chars = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(length))
  tracking_number = f"{prefix}{timestamp}{random_chars}"
  return tracking_number

def acquire_lock(key, lock_timeout_ms=1000):
  """
  Acquires a distributed lock using Redis with timeout.
  """
  r = redis.Redis(host=redis_host, port=redis_port)
  return r.hsetnx(key, "locked", lock_timeout_ms)

def release_lock(key):
  """
  Releases a distributed lock using Redis.
  """
  r = redis.Redis(host=redis_host, port=redis_port)
  r.delete(key)

def retry(max_retries=MAX_RETRIES):
  """
  Decorator to retry a function up to a specified number of times.
  """
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      for attempt in range(1, max_retries + 1):
        result = func(*args, **kwargs)
        if result is not None:
          return result
        else:
          print(f"Failed on attempt {attempt}. Retrying...")
      # Reached max retries without success
      print(f"Failed after {max_retries} retries.")
      return None
    return wrapper
  return decorator

@retry(max_retries=3)  # Set default retries here
def generate_unique_tracking_number(prefix="", length=10):
  """
  Attempts to generate a unique tracking number using Redis lock and database check.
  """
  lock_key = f"tracking_number_lock"

  if acquire_lock(lock_key):
    try:
      tracking_number = generate_tracking_number(prefix, length)
      conn = create_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT COUNT(*) FROM tracking_numbers WHERE tracking_number = ?", (tracking_number,))
      if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO tracking_numbers (tracking_number) VALUES (?)", (tracking_number,))
        conn.commit()
      else:
        tracking_number = None  # Uniqueness check failed, retry with new lock acquisition

      cursor.close()
      conn.close()

    except sqlite3.Error as e:
      print(f"Error accessing database: {e}")
    finally:
      release_lock(lock_key)

  return tracking_number

create_new_connection()
# Example usage
tracking_number = generate_unique_tracking_number("uniq-", 12)
if tracking_number:
  print(f"Generated unique tracking number: {tracking_number}")
else:
  print("Failed to acquire lock or generate unique tracking number.")

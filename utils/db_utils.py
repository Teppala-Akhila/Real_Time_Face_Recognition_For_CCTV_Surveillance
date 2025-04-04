import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        return sqlite3.connect('users.db')
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize the SQLite database with users table"""
    try:
        # Ensure the database directory exists
        db_dir = os.path.dirname('database.db')
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
        # Verify table creation
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if c.fetchone():
            logger.info("Users table exists")
        else:
            logger.error("Failed to create users table")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

def add_user(username, email, password):
    """Add a new user to the database"""
    try:
        # Initialize DB if not exists
        init_db()
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Insert new user
        c.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, hashed_password))
        
        conn.commit()
        logger.info(f"User {username} registered successfully")
        return True, "Registration successful"
    
    except sqlite3.IntegrityError as e:
        logger.error(f"Registration failed - integrity error: {e}")
        if "username" in str(e):
            return False, "Username already exists"
        elif "email" in str(e):
            return False, "Email already exists"
        return False, "Registration failed"
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()

def get_user(username):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        return user
    except sqlite3.Error as e:
        logger.error(f"Error getting user: {e}")
        return None
    finally:
        conn.close()

def verify_user(username, password):
    """Verify user credentials with detailed logging"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # First check if user exists
        c.execute('SELECT username, password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        
        if not result:
            logger.warning(f"Login failed: User '{username}' does not exist in database")
            return False
            
        stored_username, stored_password = result
        
        # Check password
        if check_password_hash(stored_password, password):
            logger.info(f"Login successful for user: {username}")
            return True
        else:
            logger.warning(f"Login failed: Incorrect password for user '{username}'")
            return False
            
    except Exception as e:
        logger.error(f"Database error during login: {e}")
        return False
    finally:
        conn.close()

def check_user_exists(username):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Check if username exists and get their details
        c.execute('''
            SELECT username, email 
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = c.fetchone()
        if user:
            logger.info(f"User found: {username}")
            return True
        else:
            logger.info(f"User not found: {username}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking user: {e}")
        return False
    finally:
        conn.close()

def reset_password(username, new_password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        hashed_password = generate_password_hash(new_password)
        c.execute('''
            UPDATE users 
            SET password = ? 
            WHERE username = ?
        ''', (hashed_password, username))
        
        if c.rowcount > 0:
            conn.commit()
            logger.info(f"Password reset successful for user: {username}")
            return True
        else:
            logger.warning(f"Password reset failed - user not found: {username}")
            return False
            
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return False
    finally:
        conn.close()

def list_all_users():
    """Debug function to list all users"""
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT username, email FROM users')
        users = c.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return [] 
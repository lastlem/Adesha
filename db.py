import sqlite3
import os

DB_PATH = 'cozy_corner.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """
    Initializes the database schema.
    Creates the 'envelopes' table with a recipient field.
    """
    with get_db_connection() as conn:
        # Create table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS envelopes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text_message TEXT NOT NULL,
                image_path TEXT,
                audio_path TEXT,
                recipient TEXT NOT NULL
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                image_path TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS character_positions (
                recipient TEXT,
                image_path TEXT,
                top TEXT,
                left TEXT,
                PRIMARY KEY (recipient, image_path)
            )
        ''')

        # Migration: Add recipient column if it doesn't exist (for older DB versions)
        try:
            conn.execute('ALTER TABLE envelopes ADD COLUMN recipient TEXT NOT NULL DEFAULT "adesha"')
        except sqlite3.OperationalError:
            # Column already exists
            pass

        # Migration: Add hidden column to character_positions if it doesn't exist
        try:
            conn.execute('ALTER TABLE character_positions ADD COLUMN hidden INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            # Column already exists
            pass

        conn.commit()
    print("Database initialized successfully.")

def get_envelopes_by_recipient(recipient):
    """Retrieves all envelopes for a specific recipient."""
    with get_db_connection() as conn:
        envelopes = conn.execute('SELECT * FROM envelopes WHERE recipient = ?', (recipient,)).fetchall()
        return [dict(envelope) for envelope in envelopes]

def get_all_envelopes():
    """Retrieves all envelopes from the database."""
    with get_db_connection() as conn:
        envelopes = conn.execute('SELECT * FROM envelopes').fetchall()
        return [dict(envelope) for envelope in envelopes]

def get_envelope_by_id(envelope_id):
    """Retrieves a single envelope by its ID."""
    with get_db_connection() as conn:
        envelope = conn.execute('SELECT * FROM envelopes WHERE id = ?', (envelope_id,)).fetchone()
        return dict(envelope) if envelope else None

def create_envelope(title, text_message, recipient, image_path=None, audio_path=None):
    """Inserts a new envelope into the database."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO envelopes (title, text_message, recipient, image_path, audio_path) VALUES (?, ?, ?, ?, ?)',
            (title, text_message, recipient, image_path, audio_path)
        )
        conn.commit()
        return cursor.lastrowid

def update_envelope(envelope_id, title, text_message, recipient, image_path=None, audio_path=None):
    """Updates an existing envelope."""
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE envelopes SET title = ?, text_message = ?, recipient = ?, image_path = ?, audio_path = ? WHERE id = ?',
            (title, text_message, recipient, image_path, audio_path, envelope_id)
        )
        conn.commit()

def delete_envelope(envelope_id):
    """Deletes an envelope from the database."""
    with get_db_connection() as conn:
        conn.execute('DELETE FROM envelopes WHERE id = ?', (envelope_id,))
        conn.commit()

def remove_character_position(recipient, image_path):
    """Removes a character's position for a specific recipient."""
    with get_db_connection() as conn:
        conn.execute('DELETE FROM character_positions WHERE recipient = ? AND image_path = ?', (recipient, image_path))
        conn.commit()

def remove_user_character(recipient, image_path):
    """Removes a user-uploaded character."""
    with get_db_connection() as conn:
        conn.execute('DELETE FROM user_characters WHERE recipient = ? AND image_path = ?', (recipient, image_path))
        conn.commit()

def is_user_character(recipient, image_path):
    """Checks if a character was uploaded by the specific user."""
    with get_db_connection() as conn:
        row = conn.execute('SELECT 1 FROM user_characters WHERE recipient = ? AND image_path = ?', (recipient, image_path)).fetchone()
        return row is not None

def get_user_characters(recipient):
    """Retrieves all characters uploaded by a specific user."""
    with get_db_connection() as conn:
        characters = conn.execute('SELECT image_path FROM user_characters WHERE recipient = ?', (recipient,)).fetchall()
        return [row['image_path'] for row in characters]

def add_user_character(recipient, image_path):
    """Adds a new character for a specific user."""
    with get_db_connection() as conn:
        conn.execute('INSERT INTO user_characters (recipient, image_path) VALUES (?, ?)', (recipient, image_path))
        conn.commit()

def get_all_character_positions(recipient):
    """Retrieves all saved character positions for a specific recipient."""
    with get_db_connection() as conn:
        positions = conn.execute('SELECT * FROM character_positions WHERE recipient = ?', (recipient,)).fetchall()
        return {row['image_path']: {'top': row['top'], 'left': row['left'], 'hidden': row['hidden']} for row in positions}

def hide_character_position(recipient, image_path):
    """Marks a character's position as hidden for a specific recipient."""
    with get_db_connection() as conn:
        conn.execute('UPDATE character_positions SET hidden = 1 WHERE recipient = ? AND image_path = ?', (recipient, image_path))
        conn.commit()

def save_character_position(recipient, image_path, top, left):
    """Saves or updates a character's position for a specific recipient."""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO character_positions (recipient, image_path, top, left)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(recipient, image_path) DO UPDATE SET top=excluded.top, left=excluded.left
        ''', (recipient, image_path, top, left))
        conn.commit()

if __name__ == "__main__":
    init_db()

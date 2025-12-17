import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from dotenv import load_dotenv
load_dotenv()
 

config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
with open(config_path) as data_file:
    config = json.load(data_file)

class PostgreSQLConnection:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Create PostgreSQL connection"""
        try:
            self.conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=os.environ.get('DB_PORT')
            )
            # Set to return dictionaries
            self.conn.cursor_factory = RealDictCursor
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def execute(self, query, params=None):
        """Execute query with SQLite to PostgreSQL parameter conversion"""
        # Convert SQLite ? placeholders to PostgreSQL %s
        if '?' in query:
            query = query.replace('?', '%s')
        
        cur = self.conn.cursor()
        try:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                return cur
            else:
                # For INSERT/UPDATE/DELETE, return self for method chaining
                return self
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def fetchall(self):
        """Fetch all results"""
        return self.conn.cursor().fetchall()
    
    def fetchone(self):
        """Fetch one result"""
        return self.conn.cursor().fetchone()
    
    @property
    def lastrowid(self):
        """Get last inserted row ID"""
        cur = self.conn.cursor()
        cur.execute("SELECT LASTVAL()")
        return cur.fetchone()['lastval']
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()

# Create global connection instance
conn = PostgreSQLConnection()

def init_database():
    """Initialize database tables"""
    try:
        # Create tables if they don't exist
        conn.execute('''CREATE TABLE IF NOT EXISTS patient
            (pat_id SERIAL PRIMARY KEY,
            pat_first_name TEXT NOT NULL,
            pat_last_name TEXT NOT NULL,
            pat_insurance_no TEXT NOT NULL,
            pat_ph_no TEXT NOT NULL,
            pat_date DATE DEFAULT CURRENT_DATE,
            pat_address TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS doctor
            (doc_id SERIAL PRIMARY KEY,
            doc_first_name TEXT NOT NULL,
            doc_last_name TEXT NOT NULL,
            doc_ph_no TEXT NOT NULL,
            doc_date DATE DEFAULT CURRENT_DATE,
            doc_address TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS nurse
            (nur_id SERIAL PRIMARY KEY,
            nur_first_name TEXT NOT NULL,
            nur_last_name TEXT NOT NULL,
            nur_ph_no TEXT NOT NULL,
            nur_date DATE DEFAULT CURRENT_DATE,
            nur_address TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS appointment
            (app_id SERIAL PRIMARY KEY,
            pat_id INTEGER NOT NULL,
            doc_id INTEGER NOT NULL,
            appointment_date DATE NOT NULL,
            FOREIGN KEY(pat_id) REFERENCES patient(pat_id),
            FOREIGN KEY(doc_id) REFERENCES doctor(doc_id))''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS room
            (room_no INTEGER PRIMARY KEY,
            room_type TEXT NOT NULL,
            available INTEGER NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS medication
            (code INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            description TEXT)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS department
            (department_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            head_id INTEGER NOT NULL,
            FOREIGN KEY(head_id) REFERENCES doctor(doc_id))''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS procedure
            (code integer PRIMARY KEY,
            name TEXT NOT NULL,
            cost INTEGER NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS undergoes
            (pat_id INTEGER NOT NULL,
            proc_code INTEGER NOT NULL,
            u_date DATE NOT NULL,
            doc_id INTEGER,
            nur_id INTEGER,
            room_no INTEGER,
            PRIMARY KEY(pat_id, proc_code, u_date),
            FOREIGN KEY(pat_id) REFERENCES patient(pat_id),
            FOREIGN KEY(proc_code) REFERENCES procedure(code),
            FOREIGN KEY(doc_id) REFERENCES doctor(doc_id),
            FOREIGN KEY(nur_id) REFERENCES nurse(nur_id),
            FOREIGN KEY(room_no) REFERENCES room(room_no))''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS prescribes
            (doc_id INTEGER,
            pat_id INTEGER,
            med_code INTEGER,
            p_date DATE NOT NULL,
            app_id INTEGER NOT NULL,
            dose INTEGER NOT NULL,
            PRIMARY KEY(doc_id, pat_id, med_code, p_date),
            FOREIGN KEY(doc_id) REFERENCES doctor(doc_id),
            FOREIGN KEY(pat_id) REFERENCES patient(pat_id),
            FOREIGN KEY(med_code) REFERENCES medication(code),
            FOREIGN KEY(app_id) REFERENCES appointment(app_id))''')
        
        conn.commit()
        print("PostgreSQL database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.conn.rollback()

# Initialize database when module is imported
init_database()
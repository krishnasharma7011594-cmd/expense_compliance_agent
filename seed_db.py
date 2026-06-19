import sqlite3
import datetime
import uuid

def seed_db():
    conn = sqlite3.connect('audit_history.db')
    c = conn.cursor()
    
    # Create tables if not exist
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                 (id TEXT PRIMARY KEY, 
                  timestamp TEXT, 
                  merchant TEXT, 
                  amount REAL, 
                  category TEXT, 
                  status TEXT, 
                  report TEXT)''')
    
    # Sample data
    data = [
        (f"TXN_{uuid.uuid4().hex[:6]}", datetime.datetime.now().isoformat(), "Amazon Cloud", 250.0, "software", "COMPLIANT", "Automated audit: Project infrastructure expense within limits."),
        (f"TXN_{uuid.uuid4().hex[:6]}", datetime.datetime.now().isoformat(), "Luxury Sushi", 320.0, "meals", "FLAGGED", "Compliance Violation: Individual meal exceeds $100 daily cap."),
        (f"TXN_{uuid.uuid4().hex[:6]}", datetime.datetime.now().isoformat(), "Starbucks", 15.50, "meals", "COMPLIANT", "Automated audit: Routine coffee expense compliant."),
        (f"TXN_{uuid.uuid4().hex[:6]}", datetime.datetime.now().isoformat(), "Vercel Pro", 20.0, "software", "COMPLIANT", "Automated audit: SaaS subscription approved.")
    ]
    
    c.executemany("INSERT OR IGNORE INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()
    print("Database seeded with real sample data.")

if __name__ == "__main__":
    seed_db()

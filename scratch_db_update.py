import sqlite3
def update_db():
    conn = sqlite3.connect('events.db')
    conn.execute("UPDATE events SET category='sports' WHERE category='parties'")
    conn.commit()
    conn.close()
    print("Database Updated to Sports")

if __name__ == '__main__':
    update_db()

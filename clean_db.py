import sqlite3

def clean():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events')
    conn.commit()
    conn.close()
    print("All mock and legacy events have been successfully removed.")

if __name__ == '__main__':
    clean()

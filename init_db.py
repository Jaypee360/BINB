import sqlite3

def init_db():
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            date_time TEXT NOT NULL
        )
    ''')

    # Clear existing data just in case
    cursor.execute('DELETE FROM events')

    # Seed data
    # We will leave "Community" and "Business" empty to demonstrate Task 3 (empty states)
    # We'll just add one event to "Sports" to show they work.
    sample_events = [
        ('Brandon Welcome Gala', 'Join us for an unforgettable night of networking, music, and great food!', 'sports', 'Tomorrow • 8:00 PM'),
        ('Tech Startup Mixer', 'A small mixer for software engineers and founders in Brandon.', 'business', 'Next Friday • 6:00 PM')
    ]

    cursor.executemany('INSERT INTO events (title, description, category, date_time) VALUES (?, ?, ?, ?)', sample_events)

    connection.commit()
    connection.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()

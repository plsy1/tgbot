import sqlite3

def initialize_database():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # 创建 Sites 表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sites (
            id INTEGER PRIMARY KEY,
            host TEXT NOT NULL,
            name TEXT NOT NULL,
            cookies TEXT NOT NULL,
            sign_in_url TEXT NOT NULL,
            sign_in_status BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


initialize_database()
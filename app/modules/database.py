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
            sign_in_status BOOLEAN NOT NULL DEFAULT 0,
            UNIQUE(host)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SiteStats (
            id INTEGER PRIMARY KEY,
            host TEXT NOT NULL,
            username TEXT,
            user_level TEXT,
            user_id TEXT,
            upload_amount TEXT,
            download_amount TEXT,
            share_ratio TEXT,
            magic_value TEXT,
            seeding_volume TEXT,
            passkey TEXT,
            FOREIGN KEY (host) REFERENCES Sites(host) ON DELETE CASCADE
        )
        ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AudioBooks (
            folder TEXT NOT NULL,
            rss_url TEXT
        )
        ''')
    
    
    
    conn.commit()
    conn.close()


def get_passkey_and_host():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT passkey,host FROM SiteStats')
        res = cursor.fetchall()
        
        return res
        
    except Exception as e:
            print(f"Error during get passkey: {str(e)}")

    finally:
            conn.close()

initialize_database()


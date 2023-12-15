import sqlite3
from app.utils.logs import log_error_info, log_background_info

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
            
            
def get_sites():

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT host, name, cookies, sign_in_url, sign_in_status FROM Sites')
        sites = cursor.fetchall()
        return sites
    except Exception as e:
            print(f"Error during get passkey: {str(e)}")
    finally:
            conn.close()


def get_sites_by_host(host):

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT host, name, cookies, sign_in_url, sign_in_status FROM Sites WHERE host = ?', (host,))
        sites = cursor.fetchall()
        return sites
    except Exception as e:
            print(f"Error during get passkey: {str(e)}")
    finally:
            conn.close()
            
            
def set_sign_in_status(host, status):
        try:
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()

            try:
                cursor.execute('''
                    UPDATE Sites
                    SET sign_in_status = ?
                    WHERE host = ?
                ''', (int(status), host)) 

                conn.commit()
                log_background_info(f"Sign-in status set to {status} for site: {host}")

            except Exception as e:

                conn.rollback()
                print(f"Error during set_sign_in_status: {str(e)}")

            finally:
                conn.close()

        except Exception as e:
            print(f"Error during set_sign_in_status: {str(e)}")
 

def clear_sign_status():
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE Sites
                SET sign_in_status = 0
            ''') 

            conn.commit()
            log_background_info("Sign-in status set to False for all sites")

        except Exception as e:

            conn.rollback()
            print(f"Error during clear_sign_in_status: {str(e)}")

        finally:
            conn.close()

    except Exception as e:
        print(f"Error during clear_sign_in_status: {str(e)}")
        
                    
initialize_database()


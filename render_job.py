import json
import psycopg2
from psycopg2.extras import execute_values
import os
import sys

def main():
    print("Loading data...")
    with open("scraped_data.json", "r") as f:
        data = json.load(f)

    print(f"Found {len(data)} items to save.")

    conn_str = os.environ.get("DATABASE_URL")
    if not conn_str:
        print("DATABASE_URL not set.")
        sys.exit(1)

    print("Connecting to DB...")
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            url VARCHAR(2048) UNIQUE NOT NULL,
            full_text TEXT NOT NULL,
            matched_content TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("Table ensured.")

    insert_query = """
    INSERT INTO documents (url, full_text, matched_content)
    VALUES %s
    ON CONFLICT (url) DO UPDATE
    SET full_text = EXCLUDED.full_text,
        matched_content = EXCLUDED.matched_content,
        created_at = CURRENT_TIMESTAMP;
    """

    values = [(item['url'], item['full_text'], item['matched_content']) for item in data]
    execute_values(cur, insert_query, values)
    conn.commit()
    print("Data inserted successfully.")

    cur.execute("SELECT COUNT(*) FROM documents;")
    count = cur.fetchone()[0]
    print(f"Total documents in database: {count}")

if __name__ == "__main__":
    main()

import os
import json
import psycopg2
from psycopg2.extras import execute_values
from http.server import BaseHTTPRequestHandler, HTTPServer

def insert_data():
    conn_str = os.environ.get("DATABASE_URL")
    if not conn_str:
        return "No DATABASE_URL"

    try:
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

        with open("scraped_data.json", "r") as f:
            data = json.load(f)

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

        cur.execute("SELECT COUNT(*) FROM documents;")
        count = cur.fetchone()[0]

        cur.close()
        conn.close()
        return f"Successfully saved {count} records."
    except Exception as e:
        return f"Error: {e}"

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if self.path == '/run':
            result = insert_data()
            self.wfile.write(f"Result: {result}".encode())
        else:
            self.wfile.write(b"Hello. Go to /run to insert data.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('', port), RequestHandler)
    print(f"Starting server on port {port}...")
    server.serve_forever()

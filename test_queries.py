import sqlite3
from sql_queries import SQL_QUERIES

def test_all_queries(db_path="database/food_wastage.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for name, query in SQL_QUERIES.items():
        print(f"\n--- {name} ---")
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error running query {name}: {e}")

    conn.close()

if __name__ == "__main__":
    test_all_queries()

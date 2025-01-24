import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # 配置连接以返回带有列名的字典
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorite (
                idx   INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                link  TEXT NOT NULL,
                tag_list  TEXT NOT NULL,
                img_url  TEXT NOT NULL,
                is_download  INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def insert(self, data_tuple: tuple) -> None:
        self.cursor.execute(
            "INSERT INTO favorite (idx, title, link, tag_list, img_url, is_download) VALUES (?, ?, ?, ?, ?, ?)",
            data_tuple)
        self.conn.commit()

    def query_index(self, index: int) -> bool:
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM favorite WHERE idx = ?)", (index,))
        exists = self.cursor.fetchone()[0]
        return exists == 1

    def query_not_download_list(self) -> list:
        self.cursor.execute("SELECT * FROM favorite WHERE is_download = 0")
        rows = self.cursor.fetchall()
        records = [dict(row) for row in rows]  # 将每一行转化为字典
        return records

    def update_download(self, idx: int) -> None:
        self.cursor.execute("UPDATE favorite SET is_download = 1 WHERE idx = ?", (idx,))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

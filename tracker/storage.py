"""순위 시계열 저장소 (SQLite, 표준 라이브러리만 사용).

매일 (date, keyword, rank) 한 행씩 적재한다. 재실행 시 같은 날짜/키워드는 덮어쓴다.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RankRow:
    date: str
    keyword: str
    rank: int | None
    found_url: str | None
    note: str


class RankStore:
    def __init__(self, db_path: str | Path = "rank_history.db"):
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rank_history (
                date       TEXT NOT NULL,   -- YYYY-MM-DD (측정일)
                keyword    TEXT NOT NULL,
                rank       INTEGER,         -- NULL = 미노출
                found_url  TEXT,
                note       TEXT,
                PRIMARY KEY (date, keyword)
            )
            """
        )
        self._conn.commit()

    def upsert(self, row: RankRow) -> None:
        self._conn.execute(
            """
            INSERT INTO rank_history (date, keyword, rank, found_url, note)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date, keyword) DO UPDATE SET
                rank=excluded.rank, found_url=excluded.found_url, note=excluded.note
            """,
            (row.date, row.keyword, row.rank, row.found_url, row.note),
        )
        self._conn.commit()

    def history(self, keyword: str, limit: int = 30) -> list[RankRow]:
        """해당 키워드의 최근 기록을 날짜 오름차순으로 반환."""
        cur = self._conn.execute(
            "SELECT * FROM rank_history WHERE keyword=? ORDER BY date DESC LIMIT ?",
            (keyword, limit),
        )
        rows = [RankRow(r["date"], r["keyword"], r["rank"], r["found_url"], r["note"])
                for r in cur.fetchall()]
        return list(reversed(rows))

    def close(self) -> None:
        self._conn.close()

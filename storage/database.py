"""Database interface for property data."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Iterator

from models.property import PropertyRecord
from models.watchlist import WatchlistEntry


class PropertyDatabase:
    """SQLite database with DuckDB analytics support."""
    
    def __init__(self, path: str | Path = "data/properties.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
    
    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.path))
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self) -> "PropertyDatabase":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
    
    def init_schema(self) -> None:
        """Initialize database schema from schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as f:
            schema = f.read()
        self.conn.executescript(schema)
    
    def __contains__(self, id: str) -> bool:
        """Check if property exists by ID."""
        cursor = self.conn.execute(
            "SELECT 1 FROM properties WHERE id = ?", (id,)
        )
        return cursor.fetchone() is not None
    
    def __getitem__(self, id: str) -> PropertyRecord | None:
        """Get property by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM properties WHERE id = ?", (id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_property(row)
    
    def __setitem__(self, id: str, record: PropertyRecord) -> bool:
        """Insert or update property record. Returns True if new."""
        existing = id in self
        now = datetime.now().isoformat()
        
        data = record.to_dict()
        data["id"] = id
        
        if existing:
            data["updated_at"] = now
        else:
            data["first_seen_at"] = now
            data["updated_at"] = now
        
        data["key_features"] = json.dumps(data["key_features"])
        data["images"] = json.dumps(data["images"])
        data["raw_data"] = json.dumps(data.get("raw_data"))
        
        columns = list(data.keys())
        placeholders = [f":{c}" for c in columns]
        
        sql = f"""
            INSERT INTO properties ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT(id) DO UPDATE SET
            {', '.join(f'{c} = :{c}' for c in columns if c != 'id')}
        """
        
        self.conn.execute(sql, data)
        self.conn.commit()
        return not existing
    
    def __delitem__(self, id: str) -> None:
        """Delete property by ID."""
        self.conn.execute("DELETE FROM properties WHERE id = ?", (id,))
        self.conn.commit()
    
    def __len__(self) -> int:
        """Count properties in database."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM properties")
        return cursor.fetchone()[0]
    
    def insert(self, record: PropertyRecord) -> bool:
        """Insert or update a property record. Returns True if new."""
        return self.__setitem__(record.id, record)
    
    def insert_many(self, records: list[PropertyRecord]) -> int:
        """Bulk insert records. Returns count of new records inserted."""
        new_count = 0
        for record in records:
            if self.insert(record):
                new_count += 1
        return new_count
    
    def get_by_id(self, id: str) -> PropertyRecord | None:
        """Get property by ID."""
        return self[id]
    
    def query(self, sql: str, params: tuple = ()) -> list[PropertyRecord]:
        """Execute raw SQL query and return PropertyRecords."""
        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()
        return [self._row_to_property(row) for row in rows]
    
    def _row_to_property(self, row: sqlite3.Row) -> PropertyRecord:
        """Convert a database row to PropertyRecord."""
        data = dict(row)
        
        if data.get("key_features"):
            try:
                data["key_features"] = json.loads(data["key_features"])
            except json.JSONDecodeError:
                data["key_features"] = []
        
        if data.get("images"):
            try:
                data["images"] = json.loads(data["images"])
            except json.JSONDecodeError:
                data["images"] = []
        
        if data.get("raw_data"):
            try:
                data["raw_data"] = json.loads(data["raw_data"])
            except json.JSONDecodeError:
                data["raw_data"] = None
        
        return PropertyRecord.from_dict(data)
    
    def iter_all(self) -> Iterator[PropertyRecord]:
        """Iterate over all properties."""
        cursor = self.conn.execute("SELECT * FROM properties")
        while True:
            rows = cursor.fetchmany(100)
            if not rows:
                break
            for row in rows:
                yield self._row_to_property(row)
    
    def where(self, **filters: Any) -> "QueryBuilder":
        """Start a query with filters."""
        return QueryBuilder(self).where(**filters)
    
    def watchlist(self) -> list[WatchlistEntry]:
        """Get all watchlist entries."""
        cursor = self.conn.execute("SELECT * FROM watchlist ORDER BY id")
        return [WatchlistEntry.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_watchlist(self, id: int) -> WatchlistEntry | None:
        """Get watchlist entry by ID."""
        cursor = self.conn.execute("SELECT * FROM watchlist WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return WatchlistEntry.from_dict(dict(row))
    
    def add_watchlist(self, entry: WatchlistEntry) -> int:
        """Add a new watchlist entry. Returns the new ID."""
        data = entry.to_dict()
        data.pop("id", None)
        
        columns = list(data.keys())
        placeholders = [f":{c}" for c in columns]
        
        sql = f"""
            INSERT INTO watchlist ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor = self.conn.execute(sql, data)
        self.conn.commit()
        return cursor.lastrowid or 0
    
    def update_watchlist(self, entry: WatchlistEntry) -> None:
        """Update an existing watchlist entry."""
        if entry.id is None:
            raise ValueError("Cannot update entry without ID")
        
        data = entry.to_dict()
        id_val = data.pop("id")
        
        columns = list(data.keys())
        set_clause = ', '.join(f'{c} = :{c}' for c in columns)
        
        sql = f"UPDATE watchlist SET {set_clause} WHERE id = :id"
        data["id"] = id_val
        
        self.conn.execute(sql, data)
        self.conn.commit()
    
    def delete_watchlist(self, id: int) -> None:
        """Delete a watchlist entry."""
        self.conn.execute("DELETE FROM watchlist WHERE id = ?", (id,))
        self.conn.commit()
    
    def get_enabled_watchlist(self) -> list[WatchlistEntry]:
        """Get all enabled watchlist entries."""
        cursor = self.conn.execute(
            "SELECT * FROM watchlist WHERE enabled = 1 ORDER BY id"
        )
        return [WatchlistEntry.from_dict(dict(row)) for row in cursor.fetchall()]


class QueryBuilder:
    """Chainable query builder for properties."""
    
    def __init__(self, db: PropertyDatabase):
        self._db = db
        self._conditions: list[str] = []
        self._params: list[Any] = []
        self._limit_val: int | None = None
        self._offset_val: int | None = None
        self._order_by: str | None = None
    
    def where(self, **filters: Any) -> "QueryBuilder":
        for key, value in filters.items():
            if value is None:
                continue
            
            if "__" in key:
                field, op = key.rsplit("__", 1)
            else:
                field, op = key, "eq"
            
            ops = {
                "eq": "=",
                "ne": "!=",
                "gt": ">",
                "gte": ">=",
                "lt": "<",
                "lte": "<=",
                "in": "IN",
                "like": "LIKE",
            }
            
            sql_op = ops.get(op, "=")
            
            if op == "in":
                placeholders = ", ".join("?" * len(value))
                self._conditions.append(f"{field} {sql_op} ({placeholders})")
                self._params.extend(value)
            else:
                self._conditions.append(f"{field} {sql_op} ?")
                self._params.append(value)
        
        return self
    
    def order_by(self, field: str, desc: bool = False) -> "QueryBuilder":
        direction = "DESC" if desc else "ASC"
        self._order_by = f"{field} {direction}"
        return self
    
    def limit(self, n: int) -> "QueryBuilder":
        self._limit_val = n
        return self
    
    def offset(self, n: int) -> "QueryBuilder":
        self._offset_val = n
        return self
    
    def all(self) -> list[PropertyRecord]:
        sql = "SELECT * FROM properties"
        
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        
        if self._order_by:
            sql += f" ORDER BY {self._order_by}"
        
        if self._limit_val is not None:
            sql += f" LIMIT {self._limit_val}"
        
        if self._offset_val is not None:
            sql += f" OFFSET {self._offset_val}"
        
        cursor = self._db.conn.execute(sql, self._params)
        return [self._db._row_to_property(row) for row in cursor.fetchall()]
    
    def first(self) -> PropertyRecord | None:
        records = self.limit(1).all()
        return records[0] if records else None
    
    def count(self) -> int:
        sql = "SELECT COUNT(*) FROM properties"
        
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        
        cursor = self._db.conn.execute(sql, self._params)
        return cursor.fetchone()[0]

import os
import sqlite3
from datetime import datetime


class DatabaseManager:
    """DatabaseManager for the SixGames SQLite database."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'sixgames.db')
        self.db_path = db_path
        self.initialize_database()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def initialize_database(self):
        conn = self._connect()
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS maze_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_level INTEGER NOT NULL DEFAULT 1,
                    highest_level INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS hangman_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_streak INTEGER NOT NULL DEFAULT 0,
                    best_streak INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS minesweeper_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_streak INTEGER NOT NULL DEFAULT 0,
                    best_streak INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    def get_maze_progress(self):
        conn = self._connect()
        try:
            row = conn.execute('''
                SELECT id, current_level, highest_level, updated_at
                FROM maze_progress
                ORDER BY id ASC
                LIMIT 1
            ''').fetchone()
            if row is None:
                return {'id': None, 'current_level': 1, 'highest_level': 1, 'updated_at': None}
            return dict(row)
        finally:
            conn.close()

    def save_maze_progress(self, current_level, highest_level=None):
        if highest_level is None:
            highest_level = current_level
        highest_level = max(1, int(highest_level))
        current_level = max(1, int(current_level))
        conn = self._connect()
        try:
            row = conn.execute('SELECT id FROM maze_progress ORDER BY id ASC LIMIT 1').fetchone()
            stamp = datetime.now().isoformat(timespec='seconds')
            if row is None:
                conn.execute('''
                    INSERT INTO maze_progress (current_level, highest_level, updated_at)
                    VALUES (?, ?, ?)
                ''', (current_level, max(highest_level, current_level), stamp))
            else:
                conn.execute('''
                    UPDATE maze_progress
                    SET current_level = ?, highest_level = ?, updated_at = ?
                    WHERE id = ?
                ''', (current_level, max(highest_level, current_level), stamp, row['id']))
            conn.commit()
        finally:
            conn.close()

    def get_hangman_stats(self):
        conn = self._connect()
        try:
            row = conn.execute('''
                SELECT id, current_streak, best_streak, updated_at
                FROM hangman_stats
                ORDER BY id ASC
                LIMIT 1
            ''').fetchone()
            if row is None:
                return {'id': None, 'current_streak': 0, 'best_streak': 0, 'updated_at': None}
            return dict(row)
        finally:
            conn.close()

    def record_hangman_win(self):
        conn = self._connect()
        try:
            row = conn.execute('SELECT id, current_streak, best_streak FROM hangman_stats ORDER BY id ASC LIMIT 1').fetchone()
            stamp = datetime.now().isoformat(timespec='seconds')
            if row is None:
                current_streak = 1
                best_streak = 1
                conn.execute('''
                    INSERT INTO hangman_stats (current_streak, best_streak, updated_at)
                    VALUES (?, ?, ?)
                ''', (current_streak, best_streak, stamp))
            else:
                current_streak = int(row['current_streak']) + 1
                best_streak = max(int(row['best_streak']), current_streak)
                conn.execute('''
                    UPDATE hangman_stats
                    SET current_streak = ?, best_streak = ?, updated_at = ?
                    WHERE id = ?
                ''', (current_streak, best_streak, stamp, row['id']))
            conn.commit()
        finally:
            conn.close()

    def record_hangman_loss(self):
        conn = self._connect()
        try:
            row = conn.execute('SELECT id, current_streak, best_streak FROM hangman_stats ORDER BY id ASC LIMIT 1').fetchone()
            stamp = datetime.now().isoformat(timespec='seconds')
            if row is None:
                conn.execute('''
                    INSERT INTO hangman_stats (current_streak, best_streak, updated_at)
                    VALUES (?, ?, ?)
                ''', (0, 0, stamp))
            else:
                conn.execute('''
                    UPDATE hangman_stats
                    SET current_streak = 0, updated_at = ?
                    WHERE id = ?
                ''', (stamp, row['id']))
            conn.commit()
        finally:
            conn.close()

    def get_minesweeper_stats(self):
        conn = self._connect()
        try:
            row = conn.execute('''
                SELECT id, current_streak, best_streak, updated_at
                FROM minesweeper_stats
                ORDER BY id ASC
                LIMIT 1
            ''').fetchone()
            if row is None:
                return {'id': None, 'current_streak': 0, 'best_streak': 0, 'updated_at': None}
            return dict(row)
        finally:
            conn.close()

    def record_minesweeper_win(self):
        conn = self._connect()
        try:
            row = conn.execute('SELECT id, current_streak, best_streak FROM minesweeper_stats ORDER BY id ASC LIMIT 1').fetchone()
            stamp = datetime.now().isoformat(timespec='seconds')
            if row is None:
                current_streak = 1
                best_streak = 1
                conn.execute('''
                    INSERT INTO minesweeper_stats (current_streak, best_streak, updated_at)
                    VALUES (?, ?, ?)
                ''', (current_streak, best_streak, stamp))
            else:
                current_streak = int(row['current_streak']) + 1
                best_streak = max(int(row['best_streak']), current_streak)
                conn.execute('''
                    UPDATE minesweeper_stats
                    SET current_streak = ?, best_streak = ?, updated_at = ?
                    WHERE id = ?
                ''', (current_streak, best_streak, stamp, row['id']))
            conn.commit()
        finally:
            conn.close()

    def record_minesweeper_loss(self):
        conn = self._connect()
        try:
            row = conn.execute('SELECT id, current_streak, best_streak FROM minesweeper_stats ORDER BY id ASC LIMIT 1').fetchone()
            stamp = datetime.now().isoformat(timespec='seconds')
            if row is None:
                conn.execute('''
                    INSERT INTO minesweeper_stats (current_streak, best_streak, updated_at)
                    VALUES (?, ?, ?)
                ''', (0, 0, stamp))
            else:
                conn.execute('''
                    UPDATE minesweeper_stats
                    SET current_streak = 0, updated_at = ?
                    WHERE id = ?
                ''', (stamp, row['id']))
            conn.commit()
        finally:
            conn.close()


# Top-level convenience inference functions requested by the project.
def initialize_database(db_path=None):
    return DatabaseManager(db_path=db_path).initialize_database()


def get_maze_progress(db_path=None):
    return DatabaseManager(db_path=db_path).get_maze_progress()


def save_maze_progress(current_level, highest_level=None, db_path=None):
    return DatabaseManager(db_path=db_path).save_maze_progress(current_level, highest_level)


def get_hangman_stats(db_path=None):
    return DatabaseManager(db_path=db_path).get_hangman_stats()


def record_hangman_win(db_path=None):
    return DatabaseManager(db_path=db_path).record_hangman_win()


def record_hangman_loss(db_path=None):
    return DatabaseManager(db_path=db_path).record_hangman_loss()


def get_minesweeper_stats(db_path=None):
    return DatabaseManager(db_path=db_path).get_minesweeper_stats()


def record_minesweeper_win(db_path=None):
    return DatabaseManager(db_path=db_path).record_minesweeper_win()


def record_minesweeper_loss(db_path=None):
    return DatabaseManager(db_path=db_path).record_minesweeper_loss()

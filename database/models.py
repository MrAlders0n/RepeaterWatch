from __future__ import annotations

import sqlite3
import threading
import time

import config


_local = threading.local()
_db_path = None


def init(db_path: str):
    global _db_path
    _db_path = db_path


def _conn() -> sqlite3.Connection:
    c = getattr(_local, "conn", None)
    if c is None:
        c = sqlite3.connect(_db_path, check_same_thread=False)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA busy_timeout=5000")
        c.row_factory = sqlite3.Row
        _local.conn = c
    return c


def aligned_ts(epoch: float | None = None) -> int:
    t = int(epoch or time.time())
    return (t // 300) * 300


# ── Device info ──────────────────────────────────────────────

def set_device_info(key: str, value: str):
    _conn().execute(
        "INSERT OR REPLACE INTO device_info (key, value) VALUES (?, ?)",
        (key, value),
    )
    _conn().commit()


def get_device_info() -> dict:
    rows = _conn().execute("SELECT key, value FROM device_info").fetchall()
    return {r["key"]: r["value"] for r in rows}


# ── Stats inserts ────────────────────────────────────────────

def insert_stats_core(ts: int, battery_mv, uptime_secs, errors, queue_len):
    _conn().execute(
        "INSERT OR REPLACE INTO stats_core (ts, battery_mv, uptime_secs, errors, queue_len) "
        "VALUES (?, ?, ?, ?, ?)",
        (ts, battery_mv, uptime_secs, errors, queue_len),
    )
    _conn().commit()


def insert_stats_radio(ts: int, noise_floor, tx_air_secs, rx_air_secs):
    _conn().execute(
        "INSERT OR REPLACE INTO stats_radio (ts, noise_floor, tx_air_secs, rx_air_secs) "
        "VALUES (?, ?, ?, ?)",
        (ts, noise_floor, tx_air_secs, rx_air_secs),
    )
    _conn().commit()


def insert_stats_packets(ts: int, recv_total, sent_total, recv_errors,
                         fwd_total, fwd_errors, direct_dups):
    _conn().execute(
        "INSERT OR REPLACE INTO stats_packets "
        "(ts, recv_total, sent_total, recv_errors, fwd_total, fwd_errors, direct_dups) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ts, recv_total, sent_total, recv_errors, fwd_total, fwd_errors, direct_dups),
    )
    _conn().commit()


def insert_stats_extpower(ts: int, channels: list[dict]):
    vals = []
    for i in range(3):
        ch = channels[i] if i < len(channels) else {}
        vals.extend([ch.get("voltage"), ch.get("current"), ch.get("power")])
    _conn().execute(
        "INSERT OR REPLACE INTO stats_extpower "
        "(ts, ch0_voltage, ch0_current, ch0_power, "
        "ch1_voltage, ch1_current, ch1_power, "
        "ch2_voltage, ch2_current, ch2_power) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ts, *vals),
    )
    _conn().commit()


def insert_packet(ts: int, direction, snr, rssi, score, hash_, path):
    _conn().execute(
        "INSERT INTO packet_log (ts, direction, snr, rssi, score, hash, path) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ts, direction, snr, rssi, score, hash_, path),
    )
    _conn().commit()


def upsert_neighbor(pubkey_prefix: str, name: str | None, last_seen: int,
                    last_snr: float | None, lat: float | None, lon: float | None):
    _conn().execute(
        "INSERT OR REPLACE INTO neighbors "
        "(pubkey_prefix, name, last_seen, last_snr, lat, lon) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (pubkey_prefix, name, last_seen, last_snr, lat, lon),
    )
    _conn().commit()


def insert_neighbor_sighting(ts: int, pubkey_prefix: str):
    _conn().execute(
        "INSERT OR IGNORE INTO neighbor_sightings (ts, pubkey_prefix) VALUES (?, ?)",
        (ts, pubkey_prefix),
    )
    _conn().commit()


# ── Queries ──────────────────────────────────────────────────

def _clamp_hours(hours: int) -> int:
    return max(1, min(hours, config.MAX_QUERY_HOURS))


def _since(hours: int) -> int:
    return aligned_ts() - _clamp_hours(hours) * 3600


def query_stats_core(hours: int = 24) -> list[dict]:
    rows = _conn().execute(
        "SELECT ts, battery_mv, uptime_secs, errors, queue_len "
        "FROM stats_core WHERE ts >= ? ORDER BY ts",
        (_since(hours),),
    ).fetchall()
    return [dict(r) for r in rows]


def query_stats_radio(hours: int = 24) -> list[dict]:
    rows = _conn().execute(
        "SELECT ts, noise_floor, tx_air_secs, rx_air_secs "
        "FROM stats_radio WHERE ts >= ? ORDER BY ts",
        (_since(hours),),
    ).fetchall()
    return [dict(r) for r in rows]


def query_stats_packets(hours: int = 24) -> list[dict]:
    rows = _conn().execute(
        "SELECT ts, recv_total, sent_total, recv_errors, fwd_total, fwd_errors, direct_dups "
        "FROM stats_packets WHERE ts >= ? ORDER BY ts",
        (_since(hours),),
    ).fetchall()
    return [dict(r) for r in rows]


def query_stats_extpower(hours: int = 24) -> list[dict]:
    rows = _conn().execute(
        "SELECT ts, ch0_voltage, ch0_current, ch0_power, "
        "ch1_voltage, ch1_current, ch1_power, "
        "ch2_voltage, ch2_current, ch2_power "
        "FROM stats_extpower WHERE ts >= ? ORDER BY ts",
        (_since(hours),),
    ).fetchall()
    return [dict(r) for r in rows]


def query_packets_recent(limit: int = 50) -> list[dict]:
    rows = _conn().execute(
        "SELECT id, ts, direction, snr, rssi, score, hash, path "
        "FROM packet_log ORDER BY id DESC LIMIT ?",
        (min(limit, 500),),
    ).fetchall()
    return [dict(r) for r in rows]


def query_packets_activity(hours: int = 24, bucket_minutes: int = 15) -> list[dict]:
    bucket_secs = max(bucket_minutes, 1) * 60
    since = _since(hours)
    rows = _conn().execute(
        "SELECT (ts / ?) * ? AS bucket, "
        "SUM(CASE WHEN direction='TX' THEN 1 ELSE 0 END) AS tx_count, "
        "SUM(CASE WHEN direction='RX' THEN 1 ELSE 0 END) AS rx_count, "
        "COUNT(*) AS total "
        "FROM packet_log WHERE ts >= ? "
        "GROUP BY bucket ORDER BY bucket",
        (bucket_secs, bucket_secs, since),
    ).fetchall()
    return [dict(r) for r in rows]


def query_neighbors() -> list[dict]:
    rows = _conn().execute(
        "SELECT pubkey_prefix, name, last_seen, last_snr, lat, lon "
        "FROM neighbors ORDER BY last_seen DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def query_neighbor_history(hours: int = 24) -> list[dict]:
    since = _since(hours)
    rows = _conn().execute(
        "SELECT ts, COUNT(DISTINCT pubkey_prefix) AS count "
        "FROM neighbor_sightings WHERE ts >= ? "
        "GROUP BY ts ORDER BY ts",
        (since,),
    ).fetchall()
    return [dict(r) for r in rows]


def query_airtime(hours: int = 24) -> list[dict]:
    rows = _conn().execute(
        "SELECT ts, tx_air_secs, rx_air_secs "
        "FROM stats_radio WHERE ts >= ? ORDER BY ts",
        (_since(hours),),
    ).fetchall()
    result = []
    prev = None
    for r in rows:
        row = dict(r)
        if prev is not None:
            dt = row["ts"] - prev["ts"]
            if dt > 0:
                tx_delta = (row["tx_air_secs"] or 0) - (prev["tx_air_secs"] or 0)
                rx_delta = (row["rx_air_secs"] or 0) - (prev["rx_air_secs"] or 0)
                result.append({
                    "ts": row["ts"],
                    "tx_pct": round(max(0, tx_delta) / dt * 100, 2),
                    "rx_pct": round(max(0, rx_delta) / dt * 100, 2),
                })
        prev = row
    return result


def db_size_bytes() -> int:
    import os
    try:
        return os.path.getsize(_db_path)
    except OSError:
        return 0

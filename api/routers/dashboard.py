"""Dashboard endpoints - Main dashboard stats and overview

OPTIMIZED: All data is loaded from database/cache instantly.
Background task updates expensive API data every 5 minutes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import psutil
import sqlite3
from datetime import datetime
import time
import json
import logging
import threading

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import get_bot_instance, get_bot_start_time

router = APIRouter()

# In-memory cache for fast access (populated by background tasks)
_cache = {
    "latency": None,
    "sonarr_status": "unknown",
    "radarr_status": "unknown",
    "last_update": 0,
}

# Background update interval (5 minutes)
BACKGROUND_UPDATE_INTERVAL = 300
_background_task_started = False


class BotStatus(BaseModel):
    online: bool
    name: str
    uptime: str
    groups: int
    users: int
    latency: Optional[float] = None


class MediaStats(BaseModel):
    sonarr_total: int
    radarr_total: int
    pending_requests: int


class GroupStats(BaseModel):
    total: int
    night_mode_enabled: int


class ResourceItem(BaseModel):
    percent: float
    label: str


class SystemResources(BaseModel):
    cpu: ResourceItem
    memory: ResourceItem
    disk: ResourceItem


class ServiceItem(BaseModel):
    name: str
    status: str
    icon: str


class DashboardData(BaseModel):
    bot_status: BotStatus
    media_stats: MediaStats
    group_stats: GroupStats
    resources: SystemResources
    services: List[ServiceItem]


def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "database",
        "group_data.db",
    )
    return sqlite3.connect(db_path)


def get_config():
    """Load config file"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config",
        "config.json",
    )
    with open(config_path, "r") as f:
        return json.load(f)


def update_background_data():
    """Background task to update expensive data (APIs, latency)"""
    global _cache
    import requests

    bot = get_bot_instance()

    # Update latency
    if bot and hasattr(bot, "token"):
        try:
            start = time.time()
            response = requests.get(
                f"https://api.telegram.org/bot{bot.token}/getMe", timeout=5
            )
            if response.status_code == 200:
                _cache["latency"] = round((time.time() - start) * 1000, 2)
        except:
            _cache["latency"] = None

    # Update Sonarr/Radarr data
    try:
        config = get_config()

        sonarr_total = 0
        radarr_total = 0
        sonarr_status = "stopped"
        radarr_status = "stopped"

        # Sonarr
        if config.get("sonarr", {}).get("URL") and config.get("sonarr", {}).get(
            "API_KEY"
        ):
            try:
                headers = {"X-Api-Key": config["sonarr"]["API_KEY"]}
                response = requests.get(
                    f"{config['sonarr']['URL']}/api/v3/series",
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 200:
                    sonarr_total = len(response.json())
                    sonarr_status = "running"
                    logger.debug(f"Sonarr API success: {sonarr_total} series")
                else:
                    logger.warning(f"Sonarr API returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Sonarr API error: {e}")

        # Radarr
        if config.get("radarr", {}).get("URL") and config.get("radarr", {}).get(
            "API_KEY"
        ):
            try:
                headers = {"X-Api-Key": config["radarr"]["API_KEY"]}
                response = requests.get(
                    f"{config['radarr']['URL']}/api/v3/movie",
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 200:
                    radarr_total = len(response.json())
                    radarr_status = "running"
                    logger.debug(f"Radarr API success: {radarr_total} movies")
                else:
                    logger.warning(f"Radarr API returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Radarr API error: {e}")

        _cache["sonarr_status"] = sonarr_status
        _cache["radarr_status"] = radarr_status

        # Save to database (counts AND status)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO dashboard_cache (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                ("sonarr_total", sonarr_total),
            )
            cursor.execute(
                "INSERT OR REPLACE INTO dashboard_cache (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                ("radarr_total", radarr_total),
            )
            # Store status as 1=running, 0=stopped
            cursor.execute(
                "INSERT OR REPLACE INTO dashboard_cache (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                ("sonarr_status", 1 if sonarr_status == "running" else 0),
            )
            cursor.execute(
                "INSERT OR REPLACE INTO dashboard_cache (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                ("radarr_status", 1 if radarr_status == "running" else 0),
            )
            conn.commit()
            conn.close()
            logger.debug(
                f"Background update: Sonarr={sonarr_total} ({sonarr_status}), Radarr={radarr_total} ({radarr_status})"
            )
        except Exception as e:
            logger.debug(f"Error saving to database: {e}")

    except Exception as e:
        logger.debug(f"Background update error: {e}")

    _cache["last_update"] = time.time()


def update_telegram_group_data():
    """Background task to update Telegram group member/admin counts"""
    import requests

    bot = get_bot_instance()
    if not bot or not hasattr(bot, "token"):
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT group_chat_id FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        groups = cursor.fetchall()

        for (group_chat_id,) in groups:
            member_count = 0
            admin_count = 0

            # Get member count
            try:
                response = requests.get(
                    f"https://api.telegram.org/bot{bot.token}/getChatMemberCount",
                    params={"chat_id": group_chat_id},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        member_count = data.get("result", 0)
            except:
                pass

            # Get admin count
            try:
                response = requests.get(
                    f"https://api.telegram.org/bot{bot.token}/getChatAdministrators",
                    params={"chat_id": group_chat_id},
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        admin_count = len(data.get("result", []))
            except:
                pass

            # Update database
            cursor.execute(
                "UPDATE group_data SET member_count = ?, admin_count = ? WHERE group_chat_id = ?",
                (member_count, admin_count, group_chat_id),
            )

        conn.commit()
        conn.close()
        logger.debug("Background update: Telegram group data refreshed")
    except Exception as e:
        logger.debug(f"Error updating Telegram group data: {e}")


def background_update_loop():
    """Continuous background update loop for all data"""
    while True:
        try:
            # Update dashboard data (Sonarr, Radarr, latency)
            update_background_data()
            # Update Telegram group data (member/admin counts)
            update_telegram_group_data()
        except Exception as e:
            logger.debug(f"Background loop error: {e}")
        time.sleep(BACKGROUND_UPDATE_INTERVAL)


def start_background_task():
    """Start background update task (called once on startup)"""
    global _background_task_started
    if not _background_task_started:
        _background_task_started = True
        # Run first update immediately in background (both dashboard and groups)
        threading.Thread(target=update_background_data, daemon=True).start()
        threading.Thread(target=update_telegram_group_data, daemon=True).start()
        # Start continuous loop
        threading.Thread(target=background_update_loop, daemon=True).start()
        logger.info(
            "Background update tasks started (Dashboard + Telegram Groups, interval: 5min)"
        )


def get_bot_status_fast() -> BotStatus:
    """Get bot status from database only (fast, no API calls)"""
    bot = get_bot_instance()
    start_time = get_bot_start_time()

    if bot and hasattr(bot, "token"):
        try:
            name = (
                f"@{bot.username}"
                if hasattr(bot, "username") and bot.username
                else "Telegram Bot"
            )
        except:
            name = "Telegram Bot"

        # Calculate uptime
        if start_time:
            uptime_seconds = (datetime.now() - start_time).total_seconds()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime = f"{hours}h {minutes}m"
        else:
            uptime = "Unknown"

        # Get data from database (fast)
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        groups = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(member_count), 0) FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        total_members = cursor.fetchone()[0]

        conn.close()

        return BotStatus(
            online=True,
            name=name,
            uptime=uptime,
            groups=groups,
            users=total_members,
            latency=_cache.get("latency"),
        )

    return BotStatus(
        online=False,
        name="Telegram Bot",
        uptime="0h 0m",
        groups=0,
        users=0,
        latency=None,
    )


def get_media_stats_fast() -> MediaStats:
    """Get media stats from database only (fast, no API calls)"""
    sonarr_total = 0
    radarr_total = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, value FROM dashboard_cache WHERE key IN ('sonarr_total', 'radarr_total')"
        )
        for row in cursor.fetchall():
            if row[0] == "sonarr_total":
                sonarr_total = row[1]
            elif row[0] == "radarr_total":
                radarr_total = row[1]
        conn.close()
    except Exception as e:
        logger.debug(f"Error loading media stats: {e}")

    return MediaStats(
        sonarr_total=sonarr_total,
        radarr_total=radarr_total,
        pending_requests=0,
    )


def get_group_stats() -> GroupStats:
    """Get group statistics from database (fast)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM group_data WHERE night_mode_active = 1")
        night_mode = cursor.fetchone()[0]

        conn.close()

        return GroupStats(total=total, night_mode_enabled=night_mode)
    except:
        return GroupStats(total=0, night_mode_enabled=0)


def get_system_resources() -> SystemResources:
    """Get system resource usage (fast, local only)"""
    # CPU - use non-blocking call
    cpu_percent = psutil.cpu_percent(interval=None)

    # Memory
    memory = psutil.virtual_memory()

    # Disk
    disk = psutil.disk_usage("/")

    return SystemResources(
        cpu=ResourceItem(
            percent=round(cpu_percent, 1),
            label=f"{cpu_percent:.1f}%",
        ),
        memory=ResourceItem(
            percent=round(memory.percent, 1),
            label=f"{memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB",
        ),
        disk=ResourceItem(
            percent=round(disk.percent, 1),
            label=f"{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB",
        ),
    )


def get_service_status_fast() -> List[ServiceItem]:
    """Get service status (fast, from cache or database)"""
    bot = get_bot_instance()

    # Get status from cache, fallback to database
    sonarr_status = _cache.get("sonarr_status")
    radarr_status = _cache.get("radarr_status")

    # If cache is empty, load from database
    if sonarr_status is None or radarr_status is None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT key, value FROM dashboard_cache WHERE key IN ('sonarr_status', 'radarr_status')"
            )
            for row in cursor.fetchall():
                if row[0] == "sonarr_status":
                    sonarr_status = "running" if row[1] == 1 else "stopped"
                elif row[0] == "radarr_status":
                    radarr_status = "running" if row[1] == 1 else "stopped"
            conn.close()
        except:
            pass

    # Default to unknown if still not set
    if sonarr_status is None:
        sonarr_status = "unknown"
    if radarr_status is None:
        radarr_status = "unknown"

    return [
        ServiceItem(
            name="Telegram Bot",
            status="running" if bot else "stopped",
            icon="fa-robot",
        ),
        ServiceItem(
            name="Web Interface",
            status="running",
            icon="fa-globe",
        ),
        ServiceItem(
            name="Sonarr",
            status=sonarr_status,
            icon="fa-tv",
        ),
        ServiceItem(
            name="Radarr",
            status=radarr_status,
            icon="fa-film",
        ),
    ]


@router.get("/", response_model=DashboardData)
async def get_dashboard():
    """Get dashboard overview data (fast, from database/cache only)"""
    # Start background task if not already running
    start_background_task()

    try:
        bot_status = get_bot_status_fast()
        media_stats = get_media_stats_fast()
        group_stats = get_group_stats()
        resources = get_system_resources()
        services = get_service_status_fast()

        return DashboardData(
            bot_status=bot_status,
            media_stats=media_stats,
            group_stats=group_stats,
            resources=resources,
            services=services,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot-status", response_model=BotStatus)
async def get_bot_status_endpoint():
    """Get bot status only"""
    return get_bot_status_fast()


@router.post("/refresh")
async def refresh_dashboard():
    """Trigger manual refresh of background data"""
    threading.Thread(target=update_background_data, daemon=True).start()
    return {"success": True, "message": "Refresh started in background"}

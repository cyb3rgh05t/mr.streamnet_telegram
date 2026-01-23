"""Dashboard endpoints - Main dashboard stats and overview"""

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
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import get_bot_instance, get_bot_start_time

router = APIRouter()

# Cache for expensive operations
_cache = {
    "media_stats": {"data": None, "timestamp": 0},
    "service_status": {"data": None, "timestamp": 0},
    "bot_status": {"data": None, "timestamp": 0},
    "cpu_percent": {"data": 0, "timestamp": 0},
}
CACHE_TTL = 60  # 60 seconds cache
CPU_CACHE_TTL = 5  # 5 seconds for CPU (updated in background)

# Start background CPU monitoring
_cpu_percent = 0


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


def get_bot_status() -> BotStatus:
    """Get bot status information with caching for expensive operations"""
    global _cache

    bot = get_bot_instance()
    start_time = get_bot_start_time()

    if bot and hasattr(bot, "token"):
        # Get bot info
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

        # Get group data from database (fast)
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        groups = cursor.fetchone()[0]
        conn.close()

        # Check if we have cached bot status for expensive operations
        now = time.time()
        cached = _cache.get("bot_status", {})

        if cached.get("data") and (now - cached.get("timestamp", 0)) < CACHE_TTL:
            # Use cached latency and user count
            latency = cached["data"].get("latency")
            total_members = cached["data"].get("users", 0)
        else:
            # Calculate latency with real Telegram API call
            latency = None
            try:
                import requests

                start = time.time()
                response = requests.get(
                    f"https://api.telegram.org/bot{bot.token}/getMe", timeout=3
                )
                if response.status_code == 200:
                    latency_ms = (time.time() - start) * 1000
                    latency = round(latency_ms, 2)
            except Exception:
                latency = None

            # Skip member count fetching - it's too slow for multiple groups
            # Just show groups count instead
            total_members = 0

            # Update cache
            _cache["bot_status"] = {
                "data": {"latency": latency, "users": total_members},
                "timestamp": now,
            }

        return BotStatus(
            online=True,
            name=name,
            uptime=uptime,
            groups=groups,
            users=total_members,
            latency=latency,
        )

    return BotStatus(
        online=False,
        name="Telegram Bot",
        uptime="0h 0m",
        groups=0,
        users=0,
        latency=None,
    )


def get_media_stats() -> MediaStats:
    """Get media statistics from Sonarr/Radarr with caching"""
    global _cache

    # Check cache
    now = time.time()
    if (
        _cache["media_stats"]["data"]
        and (now - _cache["media_stats"]["timestamp"]) < CACHE_TTL
    ):
        return _cache["media_stats"]["data"]

    sonarr_total = 0
    radarr_total = 0

    try:
        # Load config
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.json",
        )
        with open(config_path, "r") as f:
            config = json.load(f)

        import requests

        # Get Sonarr count
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
                    logger.debug(f"Sonarr: {sonarr_total} series found")
                else:
                    logger.debug(f"Sonarr API returned status {response.status_code}")
            except Exception as e:
                logger.debug(f"Sonarr API error: {e}")

        # Get Radarr count
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
                    logger.debug(f"Radarr: {radarr_total} movies found")
                else:
                    logger.debug(f"Radarr API returned status {response.status_code}")
            except Exception as e:
                logger.debug(f"Radarr API error: {e}")

    except Exception as e:
        logger.debug(f"Error loading config for media stats: {e}")

    result = MediaStats(
        sonarr_total=sonarr_total, radarr_total=radarr_total, pending_requests=0
    )

    # Update cache
    _cache["media_stats"] = {"data": result, "timestamp": now}

    return result


def get_group_stats() -> GroupStats:
    """Get group statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM group_data")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM group_data WHERE night_mode_active = 1")
    night_mode_enabled = cursor.fetchone()[0]

    conn.close()

    return GroupStats(total=total, night_mode_enabled=night_mode_enabled)


def get_system_resources() -> SystemResources:
    """Get system resource usage - non-blocking"""
    # Use non-blocking CPU measurement (instant, based on last interval)
    cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking!
    memory = psutil.virtual_memory()

    # Handle different OS for disk
    try:
        disk = psutil.disk_usage("/")
    except:
        try:
            disk = psutil.disk_usage("C:\\")
        except:
            disk = type("obj", (object,), {"percent": 0})()

    return SystemResources(
        cpu=ResourceItem(percent=cpu_percent, label="CPU"),
        memory=ResourceItem(percent=memory.percent, label="Memory"),
        disk=ResourceItem(percent=disk.percent, label="Disk"),
    )


def get_service_status() -> List[ServiceItem]:
    """Get service status with caching"""
    global _cache

    # Check cache
    now = time.time()
    if (
        _cache["service_status"]["data"]
        and (now - _cache["service_status"]["timestamp"]) < CACHE_TTL
    ):
        return _cache["service_status"]["data"]

    bot = get_bot_instance()

    # Check Sonarr/Radarr status
    sonarr_status = "stopped"
    radarr_status = "stopped"

    try:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "config.json",
        )
        with open(config_path, "r") as f:
            config = json.load(f)

        import requests

        # Check Sonarr
        if config.get("sonarr", {}).get("URL") and config.get("sonarr", {}).get(
            "API_KEY"
        ):
            try:
                headers = {"X-Api-Key": config["sonarr"]["API_KEY"]}
                response = requests.get(
                    f"{config['sonarr']['URL']}/api/v3/system/status",
                    headers=headers,
                    timeout=5,
                )
                if response.status_code == 200:
                    sonarr_status = "running"
            except:
                pass

        # Check Radarr
        if config.get("radarr", {}).get("URL") and config.get("radarr", {}).get(
            "API_KEY"
        ):
            try:
                headers = {"X-Api-Key": config["radarr"]["API_KEY"]}
                response = requests.get(
                    f"{config['radarr']['URL']}/api/v3/system/status",
                    headers=headers,
                    timeout=5,
                )
                if response.status_code == 200:
                    radarr_status = "running"
            except:
                pass
    except:
        pass

    services = [
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

    # Update cache
    _cache["service_status"] = {"data": services, "timestamp": now}

    return services


@router.get("/", response_model=DashboardData)
async def get_dashboard():
    """Get dashboard overview data"""
    try:
        bot_status = get_bot_status()
        media_stats = get_media_stats()
        group_stats = get_group_stats()
        resources = get_system_resources()
        services = get_service_status()

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
    return get_bot_status()

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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import get_bot_instance, get_bot_start_time

router = APIRouter()


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
    """Get bot status information"""
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

        # Calculate latency with real Telegram API call
        latency = None
        try:
            import requests

            start = time.time()
            # Make a real API call to Telegram (getMe) via requests
            response = requests.get(
                f"https://api.telegram.org/bot{bot.token}/getMe", timeout=5
            )
            if response.status_code == 200:
                latency_ms = (time.time() - start) * 1000
                latency = round(latency_ms, 2)
        except Exception as e:
            latency = None

        # Get group data from database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        groups = cursor.fetchone()[0]

        # Get all group chat IDs
        cursor.execute(
            "SELECT DISTINCT group_chat_id FROM group_data WHERE group_chat_id IS NOT NULL"
        )
        group_ids = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Calculate total members from all groups using Telegram API
        total_members = 0
        if group_ids:
            try:
                import requests

                for group_id in group_ids:
                    try:
                        # Get member count for each group via API
                        response = requests.get(
                            f"https://api.telegram.org/bot{bot.token}/getChatMemberCount",
                            params={"chat_id": group_id},
                            timeout=5,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("ok"):
                                total_members += data.get("result", 0)
                    except Exception:
                        pass
            except Exception:
                total_members = 0

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
    """Get media statistics"""
    # TODO: Implement actual Sonarr/Radarr API calls
    return MediaStats(sonarr_total=0, radarr_total=0, pending_requests=0)


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
    """Get system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return SystemResources(
        cpu=ResourceItem(percent=cpu_percent, label="CPU"),
        memory=ResourceItem(percent=memory.percent, label="Memory"),
        disk=ResourceItem(percent=disk.percent, label="Disk"),
    )


def get_service_status() -> List[ServiceItem]:
    """Get service status"""
    bot = get_bot_instance()
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
            name="Sonarr Integration",
            status="running",  # TODO: Check actual Sonarr status
            icon="fa-tv",
        ),
        ServiceItem(
            name="Radarr Integration",
            status="running",  # TODO: Check actual Radarr status
            icon="fa-film",
        ),
    ]
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

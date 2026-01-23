"""About page router - version info, system info, bot status"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import platform
import psutil
import os
import requests
from typing import Optional
from datetime import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import get_bot_instance, get_bot_start_time

router = APIRouter(tags=["about"])


def parse_version_file(file_path: str) -> str:
    """Parse version from version.txt file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            # Extract version number from "Version: v1.1.0" format
            for line in content.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    # Remove 'v' prefix if present
                    return version.lstrip("v")
        return "unknown"
    except:
        return "unknown"


class SystemInfo(BaseModel):
    os: str
    os_version: str
    python_version: str
    cpu_count: int
    total_memory: float


class BotStats(BaseModel):
    uptime: str
    latency: str
    groups: int
    members: int


class BotStatus(BaseModel):
    online: bool


class AboutData(BaseModel):
    version: str
    bot_status: BotStatus
    bot_stats: BotStats
    system_info: SystemInfo


class VersionInfo(BaseModel):
    local: str
    remote: str
    is_update_available: bool
    error: Optional[str] = None


@router.get("/data", response_model=AboutData)
async def get_about_data():
    """Get all about page data"""
    try:
        # Get version from file
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "version.txt"
        )
        version = parse_version_file(version_file)

        # Get system info
        system_info = SystemInfo(
            os=platform.system(),
            os_version=platform.release(),
            python_version=platform.python_version(),
            cpu_count=psutil.cpu_count() or 0,
            total_memory=round(psutil.virtual_memory().total / (1024**3), 2),  # GB
        )

        # Get bot instance
        bot = get_bot_instance()
        start_time = get_bot_start_time()

        # Get bot status
        bot_status = BotStatus(online=bot is not None and hasattr(bot, "token"))

        # Get bot stats
        if bot and hasattr(bot, "token"):
            # Calculate uptime
            if start_time:
                uptime_seconds = (datetime.now() - start_time).total_seconds()
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                uptime = (
                    f"{days}d {hours}h {minutes}m"
                    if days > 0
                    else f"{hours}h {minutes}m"
                )
            else:
                uptime = "Unknown"

            # Get latency
            try:
                import time

                start = time.time()
                response = requests.get(
                    f"https://api.telegram.org/bot{bot.token}/getMe", timeout=5
                )
                if response.status_code == 200:
                    latency_ms = (time.time() - start) * 1000
                    latency = f"{round(latency_ms, 2)}ms"
                else:
                    latency = "N/A"
            except:
                latency = "N/A"

            # Get group count and members
            import sqlite3

            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "database",
                "group_data.db",
            )
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM group_data WHERE group_chat_id IS NOT NULL"
            )
            groups = cursor.fetchone()[0]

            # Get all group IDs for members count
            cursor.execute(
                "SELECT DISTINCT group_chat_id FROM group_data WHERE group_chat_id IS NOT NULL"
            )
            group_ids = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Calculate total members
            total_members = 0
            if group_ids:
                try:
                    for group_id in group_ids:
                        try:
                            response = requests.get(
                                f"https://api.telegram.org/bot{bot.token}/getChatMemberCount",
                                params={"chat_id": group_id},
                                timeout=5,
                            )
                            if response.status_code == 200:
                                data = response.json()
                                if data.get("ok"):
                                    total_members += data.get("result", 0)
                        except:
                            pass
                except:
                    pass

            bot_stats = BotStats(
                uptime=uptime,
                latency=latency,
                groups=groups,
                members=total_members,
            )
        else:
            bot_stats = BotStats(
                uptime="0h 0m",
                latency="N/A",
                groups=0,
                members=0,
            )

        return AboutData(
            version=version,
            bot_status=bot_status,
            bot_stats=bot_stats,
            system_info=system_info,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version", response_model=VersionInfo)
async def get_version():
    """Get version information and check for updates"""
    try:
        # Read current version from version.txt
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "version.txt"
        )
        local_version = parse_version_file(version_file)

        # Fetch latest version from GitHub
        remote_version = local_version
        try:
            response = requests.get(
                "https://api.github.com/repos/cyb3rgh05t/telegram-bot/releases/latest",
                timeout=5,
            )
            if response.status_code == 200:
                latest_release = response.json()
                remote_version = latest_release.get("tag_name", "").lstrip("v")
        except Exception:
            pass  # Use local version as fallback

        # Compare versions
        is_update_available = False
        if remote_version != "unknown" and local_version != "unknown":
            # Simple version comparison (works for semantic versioning)
            try:
                local_parts = [int(x) for x in local_version.split(".")]
                remote_parts = [int(x) for x in remote_version.split(".")]
                is_update_available = remote_parts > local_parts
            except:
                is_update_available = remote_version != local_version

        return VersionInfo(
            local=local_version,
            remote=remote_version,
            is_update_available=is_update_available,
        )
    except Exception as e:
        return VersionInfo(
            local="unknown",
            remote="unknown",
            is_update_available=False,
            error=str(e),
        )

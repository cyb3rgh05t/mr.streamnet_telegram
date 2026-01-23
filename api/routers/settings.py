"""Settings endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
import sys
import threading
import time
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.routers.auth import get_current_user, User

router = APIRouter()

# Flag to track if restart is pending
_restart_pending = False


class SettingsData(BaseModel):
    bot: Dict[str, Any]
    commands: Dict[str, str]
    welcome: Dict[str, str]
    nightmode: Dict[str, str]
    tmdb: Dict[str, str]
    sonarr: Dict[str, str]
    radarr: Dict[str, str]
    web: Dict[str, Any]


class SettingsUpdate(BaseModel):
    section: str
    key: str
    value: Any


def get_config_path():
    """Get config file path"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config",
        "config.json",
    )


@router.get("/", response_model=SettingsData)
async def get_settings(current_user: User = Depends(get_current_user)):
    """Get all settings"""
    try:
        with open(get_config_path(), "r") as f:
            config = json.load(f)

        return SettingsData(
            bot=config.get("bot", {}),
            commands=config.get("commands", {}),
            welcome=config.get("welcome", {}),
            nightmode=config.get("nightmode", {}),
            tmdb=config.get("tmdb", {}),
            sonarr=config.get("sonarr", {}),
            radarr=config.get("radarr", {}),
            web=config.get("web", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_setting(
    update: SettingsUpdate, current_user: User = Depends(get_current_user)
):
    """Update a single setting"""
    try:
        config_path = get_config_path()

        with open(config_path, "r") as f:
            config = json.load(f)

        if update.section not in config:
            raise HTTPException(status_code=404, detail="Section not found")

        config[update.section][update.key] = update.value

        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        return {"success": True, "message": "Setting updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_settings(
    settings: SettingsData, current_user: User = Depends(get_current_user)
):
    """Save all settings"""
    try:
        config_path = get_config_path()

        config = {
            "bot": settings.bot,
            "commands": settings.commands,
            "welcome": settings.welcome,
            "nightmode": settings.nightmode,
            "tmdb": settings.tmdb,
            "sonarr": settings.sonarr,
            "radarr": settings.radarr,
            "web": settings.web,
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        # Update TMDb language in database if changed
        if "DEFAULT_LANGUAGE" in settings.tmdb:
            update_tmdb_language_in_db(settings.tmdb["DEFAULT_LANGUAGE"])

        # Schedule bot restart in background
        logger.info("[WebUI] Settings saved - scheduling bot restart in 2 seconds...")
        threading.Thread(target=schedule_bot_restart, daemon=True).start()

        return {
            "success": True,
            "message": "Settings saved successfully. Bot is restarting...",
            "restarting": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def schedule_bot_restart():
    """Schedule a bot restart after a short delay"""
    global _restart_pending

    if _restart_pending:
        return

    _restart_pending = True

    # Wait 2 seconds to allow the API response to be sent
    time.sleep(2)

    logger.info("[WebUI] Restarting bot process...")

    # Restart the Python process
    try:
        python = sys.executable
        os.execv(python, [python] + sys.argv)
    except Exception as e:
        logger.error(f"[WebUI] Failed to restart bot: {e}")
        _restart_pending = False


def update_tmdb_language_in_db(language: str):
    """Update TMDb language in all group_data entries"""
    try:
        import sqlite3

        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "database",
            "group_data.db",
        )

        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Update all groups with the new language
            cursor.execute(
                "UPDATE group_data SET language = ? WHERE group_chat_id IS NOT NULL",
                (language,),
            )

            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error updating TMDb language in database: {e}")

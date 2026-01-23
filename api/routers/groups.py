"""Groups endpoints - Telegram group management"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import sqlite3
import os
import sys
import logging
import threading

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.routers.auth import get_current_user, User
from api.main import get_bot_instance
from api.routers.cache import set_total_members

router = APIRouter()


class GroupStats(BaseModel):
    member_count: int
    admin_count: int
    created_at: Optional[str]
    last_activity: Optional[str]


class GroupItem(BaseModel):
    id: int
    group_chat_id: int
    group_name: Optional[str]
    language: Optional[str]
    night_mode_active: bool
    pause_active: bool
    stats: Optional[GroupStats] = None


class GroupsResponse(BaseModel):
    groups: List[GroupItem]
    total: int


class GroupUpdate(BaseModel):
    group_chat_id: int
    field: str
    value: Any


class GroupPause(BaseModel):
    group_chat_id: int
    pause: bool


def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "database",
        "group_data.db",
    )
    return sqlite3.connect(db_path)


async def get_group_stats(group_chat_id: int) -> Optional[GroupStats]:
    """Get statistics for a group from Telegram API"""
    try:
        bot = get_bot_instance()
        if not bot:
            return None

        import requests

        # Get member count
        member_count = 0
        admin_count = 0
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

        return GroupStats(
            member_count=member_count,
            admin_count=admin_count,
            created_at=None,
            last_activity=None,
        )
    except:
        return None


@router.get("/", response_model=GroupsResponse)
async def get_groups(current_user: User = Depends(get_current_user)):
    """Get all groups with statistics (fast, from database)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Include member_count and admin_count from database
        cursor.execute(
            """
            SELECT id, group_chat_id, group_name, language, night_mode_active, 
                   COALESCE(pause_active, 0), COALESCE(member_count, 0), COALESCE(admin_count, 0)
            FROM group_data
            ORDER BY group_name
        """
        )

        rows = cursor.fetchall()
        conn.close()

        groups = []
        total_members = 0
        for row in rows:
            member_count = row[6] if row[6] else 0
            admin_count = row[7] if row[7] else 0
            total_members += member_count

            # Use cached stats from database instead of live API calls
            stats = (
                GroupStats(
                    member_count=member_count,
                    admin_count=admin_count,
                    created_at=None,
                    last_activity=None,
                )
                if row[1]
                else None
            )  # Only if group_chat_id exists

            groups.append(
                GroupItem(
                    id=row[0],
                    group_chat_id=row[1],
                    group_name=row[2],
                    language=row[3],
                    night_mode_active=bool(row[4]),
                    pause_active=bool(row[5]),
                    stats=stats,
                )
            )

        # Cache total member count for dashboard
        set_total_members(total_members)

        return GroupsResponse(groups=groups, total=len(groups))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}", response_model=GroupItem)
async def get_group(group_id: int, current_user: User = Depends(get_current_user)):
    """Get single group"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, group_chat_id, group_name, language, night_mode_active, COALESCE(pause_active, 0)
            FROM group_data
            WHERE id = ?
        """,
            (group_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Group not found")

        return GroupItem(
            id=row[0],
            group_chat_id=row[1],
            group_name=row[2],
            language=row[3],
            night_mode_active=bool(row[4]),
            pause_active=bool(row[5]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_group(
    update: GroupUpdate, current_user: User = Depends(get_current_user)
):
    """Update group field (night_mode_active only updates database for auto scheduling)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        allowed_fields = ["language", "night_mode_active"]
        if update.field not in allowed_fields:
            raise HTTPException(status_code=400, detail="Invalid field")

        # Night mode now only updates the database setting for automatic scheduling
        # No immediate Telegram API calls - the bot's scheduler will handle it based on configured times

        if update.field == "night_mode_active":
            status = "enabled" if update.value else "disabled"
            logger.info(
                f"[WebUI] Auto Night Mode {status} for GROUP CHAT ID: {update.group_chat_id}"
            )

        query = f"UPDATE group_data SET {update.field} = ? WHERE group_chat_id = ?"
        cursor.execute(query, (update.value, update.group_chat_id))

        conn.commit()
        conn.close()

        logger.debug(
            f"[WebUI] Group updated: {update.field} = {update.value} for GROUP CHAT ID: {update.group_chat_id}"
        )

        return {"success": True, "message": "Group updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause")
async def pause_group(
    pause_data: GroupPause, current_user: User = Depends(get_current_user)
):
    """Manually pause/resume a group immediately"""
    try:
        import requests

        conn = get_db_connection()
        cursor = conn.cursor()

        bot = get_bot_instance()
        if bot:
            try:
                if pause_data.pause:
                    logger.info(
                        f"[WebUI] Manual PAUSE triggered for GROUP CHAT ID: {pause_data.group_chat_id}"
                    )
                    # Send pause message to group
                    message_text = (
                        "⏸️ <b>Gruppe pausiert</b>\n\n"
                        "Die Gruppe wurde manuell pausiert. "
                        "Während dieser Zeit können nur Administratoren Nachrichten senden.\n\n"
                        "Ein Admin kann die Gruppe jederzeit wieder aktivieren."
                    )

                    requests.post(
                        f"https://api.telegram.org/bot{bot.token}/sendMessage",
                        json={
                            "chat_id": pause_data.group_chat_id,
                            "text": message_text,
                            "parse_mode": "HTML",
                        },
                        timeout=5,
                    )

                    # Restrict all members (only admins can send messages)
                    requests.post(
                        f"https://api.telegram.org/bot{bot.token}/setChatPermissions",
                        json={
                            "chat_id": pause_data.group_chat_id,
                            "permissions": {
                                "can_send_messages": False,
                                "can_send_media_messages": False,
                                "can_send_polls": False,
                                "can_send_other_messages": False,
                                "can_add_web_page_previews": False,
                                "can_change_info": False,
                                "can_invite_users": False,
                                "can_pin_messages": False,
                            },
                        },
                        timeout=5,
                    )
                else:
                    logger.info(
                        f"[WebUI] Manual RESUME triggered for GROUP CHAT ID: {pause_data.group_chat_id}"
                    )
                    # Send resume message
                    message_text = (
                        "▶️ <b>Gruppe wieder aktiv</b>\n\n"
                        "Die Gruppe wurde wieder aktiviert. Alle Mitglieder können nun wieder Nachrichten senden."
                    )

                    requests.post(
                        f"https://api.telegram.org/bot{bot.token}/sendMessage",
                        json={
                            "chat_id": pause_data.group_chat_id,
                            "text": message_text,
                            "parse_mode": "HTML",
                        },
                        timeout=5,
                    )

                    # Restore normal permissions
                    requests.post(
                        f"https://api.telegram.org/bot{bot.token}/setChatPermissions",
                        json={
                            "chat_id": pause_data.group_chat_id,
                            "permissions": {
                                "can_send_messages": True,
                                "can_send_media_messages": True,
                                "can_send_polls": True,
                                "can_send_other_messages": True,
                                "can_add_web_page_previews": True,
                                "can_change_info": False,
                                "can_invite_users": True,
                                "can_pin_messages": False,
                            },
                        },
                        timeout=5,
                    )
            except Exception as e:
                logger.error(
                    f"[WebUI] Error updating Telegram group permissions for GROUP CHAT ID {pause_data.group_chat_id}: {e}"
                )

        # Update database
        cursor.execute(
            "UPDATE group_data SET pause_active = ? WHERE group_chat_id = ?",
            (1 if pause_data.pause else 0, pause_data.group_chat_id),
        )

        conn.commit()
        conn.close()

        action = "PAUSED" if pause_data.pause else "RESUMED"
        logger.info(
            f"[WebUI] Group {action} successfully for GROUP CHAT ID: {pause_data.group_chat_id}"
        )

        return {
            "success": True,
            "message": "Group paused" if pause_data.pause else "Group resumed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def refresh_member_counts_background():
    """Background task to refresh member and admin counts from Telegram API"""
    import requests

    try:
        bot = get_bot_instance()
        if not bot:
            return

        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "database",
            "group_data.db",
        )
        conn = sqlite3.connect(db_path)
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
        logger.info("[WebUI] Member and admin counts refreshed from Telegram API")
    except Exception as e:
        logger.error(f"[WebUI] Error refreshing counts: {e}")


@router.post("/refresh")
async def refresh_groups(current_user: User = Depends(get_current_user)):
    """Trigger background refresh of member counts from Telegram API"""
    threading.Thread(target=refresh_member_counts_background, daemon=True).start()
    return {"success": True, "message": "Refresh started in background"}

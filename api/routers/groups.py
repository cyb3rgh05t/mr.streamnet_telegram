"""Groups endpoints - Telegram group management"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.routers.auth import get_current_user, User
from api.main import get_bot_instance

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
    stats: Optional[GroupStats] = None


class GroupsResponse(BaseModel):
    groups: List[GroupItem]
    total: int


class GroupUpdate(BaseModel):
    group_chat_id: int
    field: str
    value: Any


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
    """Get all groups with statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, group_chat_id, group_name, language, night_mode_active
            FROM group_data
            ORDER BY group_name
        """
        )

        rows = cursor.fetchall()
        conn.close()

        groups = []
        for row in rows:
            stats = await get_group_stats(row[1])
            groups.append(
                GroupItem(
                    id=row[0],
                    group_chat_id=row[1],
                    group_name=row[2],
                    language=row[3],
                    night_mode_active=bool(row[4]),
                    stats=stats,
                )
            )

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
            SELECT id, group_chat_id, group_name, language, night_mode_active
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
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_group(
    update: GroupUpdate, current_user: User = Depends(get_current_user)
):
    """Update group field"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        allowed_fields = ["language", "night_mode_active"]
        if update.field not in allowed_fields:
            raise HTTPException(status_code=400, detail="Invalid field")

        # Handle night mode toggle with Telegram integration
        if update.field == "night_mode_active":
            bot = get_bot_instance()
            if bot:
                try:
                    import requests

                    # Check if we're enabling night mode
                    if update.value:
                        # Send pause message to group
                        message_text = (
                            "🌙 <b>Night Mode aktiviert</b>\n\n"
                            "Die Gruppe befindet sich jetzt im Pausenmodus. "
                            "Während dieser Zeit können nur Administratoren Nachrichten senden.\n\n"
                            "Night Mode wird automatisch deaktiviert, wenn die konfigurierte Zeit endet."
                        )

                        requests.post(
                            f"https://api.telegram.org/bot{bot.token}/sendMessage",
                            json={
                                "chat_id": update.group_chat_id,
                                "text": message_text,
                                "parse_mode": "HTML",
                            },
                            timeout=5,
                        )

                        # Restrict all members (only admins can send messages)
                        requests.post(
                            f"https://api.telegram.org/bot{bot.token}/setChatPermissions",
                            json={
                                "chat_id": update.group_chat_id,
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
                        # Send resume message
                        message_text = (
                            "☀️ <b>Night Mode deaktiviert</b>\n\n"
                            "Die Gruppe ist wieder aktiv. Alle Mitglieder können nun wieder Nachrichten senden."
                        )

                        requests.post(
                            f"https://api.telegram.org/bot{bot.token}/sendMessage",
                            json={
                                "chat_id": update.group_chat_id,
                                "text": message_text,
                                "parse_mode": "HTML",
                            },
                            timeout=5,
                        )

                        # Restore normal permissions
                        requests.post(
                            f"https://api.telegram.org/bot{bot.token}/setChatPermissions",
                            json={
                                "chat_id": update.group_chat_id,
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
                    print(f"Error updating Telegram group permissions: {e}")

        query = f"UPDATE group_data SET {update.field} = ? WHERE group_chat_id = ?"
        cursor.execute(query, (update.value, update.group_chat_id))

        conn.commit()
        conn.close()

        return {"success": True, "message": "Group updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

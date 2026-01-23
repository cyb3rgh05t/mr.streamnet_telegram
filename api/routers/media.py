"""Media endpoints - Sonarr/Radarr integration"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import os
import sys
import time
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.routers.auth import get_current_user, User

router = APIRouter()

# Server-side cache for media data
_media_cache = {
    "sonarr": {"data": None, "timestamp": 0},
    "radarr": {"data": None, "timestamp": 0},
}
MEDIA_CACHE_TTL = 120  # 2 minutes cache


class MediaItem(BaseModel):
    id: int
    title: str
    year: Optional[int]
    status: str
    poster: Optional[str]
    type: str  # 'movie' or 'series'


class MediaResponse(BaseModel):
    items: List[MediaItem]
    total: int


class TMDBSearchResult(BaseModel):
    id: int
    title: str
    overview: str
    poster_path: Optional[str]
    release_date: Optional[str]
    vote_average: float


def get_config():
    """Load config"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config",
        "config.json",
    )
    with open(config_path, "r") as f:
        return json.load(f)


@router.get("/sonarr", response_model=MediaResponse)
async def get_sonarr_media(
    page: int = Query(1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get Sonarr series with server-side caching"""
    global _media_cache

    try:
        config = get_config()

        # Check if Sonarr is configured
        if (
            "sonarr" not in config
            or not config["sonarr"].get("URL")
            or not config["sonarr"].get("API_KEY")
        ):
            return MediaResponse(items=[], total=0)

        # Check cache first
        now = time.time()
        if (
            _media_cache["sonarr"]["data"]
            and (now - _media_cache["sonarr"]["timestamp"]) < MEDIA_CACHE_TTL
        ):
            items = _media_cache["sonarr"]["data"]
            logger.debug(f"Sonarr: Returning {len(items)} cached items")
        else:
            sonarr_url = config["sonarr"]["URL"]
            sonarr_api_key = config["sonarr"]["API_KEY"]

            headers = {"X-Api-Key": sonarr_api_key}
            response = requests.get(
                f"{sonarr_url}/api/v3/series", headers=headers, timeout=15
            )
            response.raise_for_status()

            series = response.json()

            items = [
                MediaItem(
                    id=s.get("id", 0),
                    title=s.get("title", "Unknown"),
                    year=s.get("year"),
                    status=s.get("status", "unknown"),
                    poster=(
                        next(
                            (
                                img.get("remoteUrl")
                                for img in s.get("images", [])
                                if img.get("coverType") == "poster"
                            ),
                            None,
                        )
                    ),
                    type="series",
                )
                for s in series
            ]

            # Update cache
            _media_cache["sonarr"] = {"data": items, "timestamp": now}
            logger.debug(f"Sonarr: Fetched and cached {len(items)} items")

        # Apply search filter
        if search:
            items = [i for i in items if search.lower() in i.title.lower()]

        return MediaResponse(items=items, total=len(items))
    except requests.exceptions.RequestException as e:
        logger.debug(f"Sonarr API error: {e}")
        return MediaResponse(items=[], total=0)
    except Exception as e:
        logger.debug(f"Sonarr error: {e}")
        return MediaResponse(items=[], total=0)


@router.get("/radarr", response_model=MediaResponse)
async def get_radarr_media(
    page: int = Query(1),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get Radarr movies with server-side caching"""
    global _media_cache

    try:
        config = get_config()

        # Check if Radarr is configured
        if (
            "radarr" not in config
            or not config["radarr"].get("URL")
            or not config["radarr"].get("API_KEY")
        ):
            return MediaResponse(items=[], total=0)

        # Check cache first
        now = time.time()
        if (
            _media_cache["radarr"]["data"]
            and (now - _media_cache["radarr"]["timestamp"]) < MEDIA_CACHE_TTL
        ):
            items = _media_cache["radarr"]["data"]
            logger.debug(f"Radarr: Returning {len(items)} cached items")
        else:
            radarr_url = config["radarr"]["URL"]
            radarr_api_key = config["radarr"]["API_KEY"]

            headers = {"X-Api-Key": radarr_api_key}
            response = requests.get(
                f"{radarr_url}/api/v3/movie", headers=headers, timeout=15
            )
            response.raise_for_status()

            movies = response.json()

            items = [
                MediaItem(
                    id=m.get("id", 0),
                    title=m.get("title", "Unknown"),
                    year=m.get("year"),
                    status=m.get("status", "unknown"),
                    poster=(
                        m.get("images", [{}])[0].get("remoteUrl")
                        if m.get("images")
                        else None
                    ),
                    type="movie",
                )
                for m in movies
            ]

            # Update cache
            _media_cache["radarr"] = {"data": items, "timestamp": now}
            logger.debug(f"Radarr: Fetched and cached {len(items)} items")

        # Apply search filter
        if search:
            items = [i for i in items if search.lower() in i.title.lower()]

        return MediaResponse(items=items, total=len(items))
    except requests.exceptions.RequestException as e:
        logger.debug(f"Radarr API error: {e}")
        return MediaResponse(items=[], total=0)
    except Exception as e:
        logger.debug(f"Radarr error: {e}")
        return MediaResponse(items=[], total=0)


@router.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(...),
    media_type: str = Query("movie"),
    current_user: User = Depends(get_current_user),
):
    """Search TMDB"""
    try:
        config = get_config()
        tmdb_api_key = config["tmdb"]["API_KEY"]
        language = config["tmdb"].get("DEFAULT_LANGUAGE", "en")

        endpoint = "tv" if media_type == "tv" else "movie"
        url = f"https://api.themoviedb.org/3/search/{endpoint}"

        params = {"api_key": tmdb_api_key, "query": query, "language": language}

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            "results": data.get("results", []),
            "total": data.get("total_results", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

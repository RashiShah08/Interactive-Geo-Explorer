from urllib.parse import quote

from fastapi import APIRouter

from server.schemas import PlaceOut
from src.data.india_states import INDIA_STATES
from src.data.models import GeoPlace
from src.data.world_landmarks import WORLD_LANDMARKS

router = APIRouter(prefix="/places", tags=["places"])


def _serialize(places: list[GeoPlace]) -> list[PlaceOut]:
    return [
        PlaceOut(
            key=place.key,
            title=place.title,
            description=place.description,
            image_url=f"/images/{quote(place.image_file)}",
            lat=place.lat,
            lon=place.lon,
            category=place.category,
        )
        for place in places
    ]


# Public: these are reference facts, not user data.
@router.get("/world", response_model=list[PlaceOut])
def world_places() -> list[PlaceOut]:
    return _serialize(WORLD_LANDMARKS)


@router.get("/india", response_model=list[PlaceOut])
def india_places() -> list[PlaceOut]:
    return _serialize(INDIA_STATES)

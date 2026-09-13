from dataclasses import dataclass


@dataclass(frozen=True)
class GeoPlace:
    """A single point of interest shown on a Folium map."""

    key: str
    title: str
    description: str
    image_file: str
    lat: float
    lon: float
    category: str

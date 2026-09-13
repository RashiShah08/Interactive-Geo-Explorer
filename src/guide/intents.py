"""Structured questions answered by computing over the records rather than by
retrieving prose: counts, locations, superlatives, distances, comparisons.

Every answer here is derived arithmetic on the corpus, so it is either correct
or absent — there is nothing for the guide to invent.
"""
import math
import re

from src.guide.index import Document, PlaceIndex


def _coord(place) -> str:
    return (
        f"{abs(place.lat):.4f}° {'N' if place.lat >= 0 else 'S'}, "
        f"{abs(place.lon):.4f}° {'E' if place.lon >= 0 else 'W'}"
    )


def haversine_km(a, b) -> float:
    radius = 6371.0
    lat1, lat2 = math.radians(a.lat), math.radians(b.lat)
    dlat = lat2 - lat1
    dlon = math.radians(b.lon - a.lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(h))


def _match_category(index: PlaceIndex, question: str) -> str | None:
    lowered = question.lower()
    # Longest first, so "South India" wins over a bare "India".
    for category in sorted(index.categories(), key=len, reverse=True):
        if category.lower() in lowered:
            return category
    return None


def _best_place(index: PlaceIndex, question: str) -> Document | None:
    hits = index.search(question, limit=1)
    return hits[0].document if hits and hits[0].score > 0.12 else None


def _distance_pair(index: PlaceIndex, question: str):
    """Handles 'between X and Y', 'from X to Y' and 'how far is X from Y'."""
    patterns = (
        r"(?:between|from)\s+(.+?)\s+(?:and|to|from)\s+(.+?)[?.]?$",
        r"\b(?:how far|distance)\b.*?\b(?:is|are)?\s*(.+?)\s+(?:from|to)\s+(.+?)[?.]?$",
    )
    for pattern in patterns:
        found = re.search(pattern, question, re.I)
        if not found:
            continue
        first = _best_place(index, found.group(1))
        second = _best_place(index, found.group(2))
        if first and second and first is not second:
            return first, second
    return None


def _listing(docs: list[Document], limit: int = 12) -> str:
    names = [doc.place.title for doc in docs]
    shown = names[:limit]
    tail = "" if len(names) <= limit else f", and {len(names) - limit} more"
    return ", ".join(shown) + tail


# ---------------------------------------------------------------- handlers


def count_intent(index: PlaceIndex, question: str):
    if not re.search(r"\bhow many\b|\bcount\b|\bnumber of\b", question, re.I):
        return None

    category = _match_category(index, question)
    if category:
        docs = index.by_category(category)
        return (f"There are {len(docs)} in {category}: {_listing(docs)}.", docs[:6])

    if re.search(r"\bstates?\b|\but\b|\bindia\b", question, re.I):
        docs = [d for d in index.documents if d.atlas == "india"]
        return (f"The India atlas holds {len(docs)} states and union territories.", docs[:6])

    if re.search(r"\blandmarks?\b|\bworld\b|\bplaces?\b|\brecords?\b", question, re.I):
        world = [d for d in index.documents if d.atlas == "world"]
        return (
            f"There are {len(index.documents)} records in total — {len(world)} world "
            f"landmarks and {len(index.documents) - len(world)} Indian states and UTs.",
            world[:6],
        )
    return None


def where_intent(index: PlaceIndex, question: str):
    if not re.search(r"\bwhere\b|\blocat|\bcoordinat|\bhow far\b|\bdistance\b", question, re.I):
        return None

    pair = _distance_pair(index, question)
    if pair:
        first, second = pair
        km = haversine_km(first.place, second.place)
        return (
            f"{first.place.title} and {second.place.title} are about "
            f"{km:,.0f} km apart in a straight line.",
            [first, second],
        )

    doc = _best_place(index, question)
    if doc:
        return (
            f"{doc.place.title} sits at {_coord(doc.place)}, filed under {doc.place.category}.",
            [doc],
        )
    return None


def nearest_intent(index: PlaceIndex, question: str):
    if not re.search(r"\bnearest\b|\bclosest\b|\bnear to\b|\bnearby\b", question, re.I):
        return None

    target = re.sub(r".*\b(?:nearest|closest|near to|nearby)\b\s*(?:to|from)?\s*", "", question, flags=re.I)
    doc = _best_place(index, target) or _best_place(index, question)
    if not doc:
        return None

    others = [d for d in index.documents if d is not doc]
    ranked = sorted(others, key=lambda other: haversine_km(doc.place, other.place))[:3]
    lines = ", ".join(
        f"{other.place.title} ({haversine_km(doc.place, other.place):,.0f} km)"
        for other in ranked
    )
    return (f"Closest to {doc.place.title}: {lines}.", [doc, *ranked])


def superlative_intent(index: PlaceIndex, question: str):
    directions = {
        r"\bnorthern?most\b|\bfarthest north\b": ("northernmost", lambda d: -d.place.lat),
        r"\bsouthern?most\b|\bfarthest south\b": ("southernmost", lambda d: d.place.lat),
        r"\beastern?most\b|\bfarthest east\b": ("easternmost", lambda d: -d.place.lon),
        r"\bwestern?most\b|\bfarthest west\b": ("westernmost", lambda d: d.place.lon),
    }
    for pattern, (label, key) in directions.items():
        if re.search(pattern, question, re.I):
            pool = index.documents
            category = _match_category(index, question)
            if category:
                pool = index.by_category(category)
            elif re.search(r"\bindia\b", question, re.I):
                pool = [d for d in index.documents if d.atlas == "india"]

            doc = sorted(pool, key=key)[0]
            return (
                f"The {label} record here is {doc.place.title}, at {_coord(doc.place)}.",
                [doc],
            )
    return None


def list_intent(index: PlaceIndex, question: str):
    if not re.search(r"\blist\b|\bshow\b|\bwhat(?:'s| is| are)\b|\bwhich\b", question, re.I):
        return None

    category = _match_category(index, question)
    if not category:
        return None

    docs = index.by_category(category)
    return (f"{len(docs)} records are filed under {category}: {_listing(docs)}.", docs[:6])


def compare_intent(index: PlaceIndex, question: str):
    pair = re.search(r"\bcompare\b\s+(.+?)\s+(?:and|with|vs\.?|versus)\s+(.+?)[?.]?$", question, re.I)
    if not pair:
        return None

    first = _best_place(index, pair.group(1))
    second = _best_place(index, pair.group(2))
    if not first or not second or first is second:
        return None

    km = haversine_km(first.place, second.place)
    return (
        f"{first.place.title} ({first.place.category}, {_coord(first.place)}) versus "
        f"{second.place.title} ({second.place.category}, {_coord(second.place)}) — "
        f"about {km:,.0f} km apart.\n\n"
        f"{first.place.title}: {first.place.description}\n\n"
        f"{second.place.title}: {second.place.description}",
        [first, second],
    )


# Words that describe wanting information rather than naming what is wanted.
GENERIC = frozenset(
    """
    place places record records atlas atlas map maps entry entries
    india indian world globe here about overview
    """.split()
)


def _region_breakdown(index: PlaceIndex, atlas: str) -> str:
    counts: dict[str, int] = {}
    for doc in index.documents:
        if doc.atlas == atlas:
            counts[doc.place.category] = counts.get(doc.place.category, 0) + 1
    ordered = sorted(counts.items(), key=lambda row: (-row[1], row[0]))
    return ", ".join(f"{name} ({number})" for name, number in ordered)


def overview_intent(index: PlaceIndex, question: str):
    """'tell me about India' is a question about the atlas, not about one record."""
    from src.guide.text import tokenise

    content = [token for token in tokenise(question) if token not in GENERIC]
    if content:
        return None  # they named something specific; let retrieval handle it

    lowered = question.lower()
    wants_india = "india" in lowered
    wants_world = "world" in lowered or "globe" in lowered

    if wants_india and not wants_world:
        docs = [d for d in index.documents if d.atlas == "india"]
        return (
            f"The India atlas holds {len(docs)} states and union territories, each with one "
            f"world record — {_region_breakdown(index, 'india')}.\n\n"
            "Ask about any of them by name, or try “what's in South India”, "
            "“the northernmost place in India”, or “what is nearest to Goa”.",
            docs[:6],
        )

    if wants_world:
        docs = [d for d in index.documents if d.atlas == "world"]
        return (
            f"The world atlas holds {len(docs)} landmarks — {_region_breakdown(index, 'world')}."
            "\n\nAsk about any of them by name, or try “how far is the Eiffel Tower from the "
            "Colosseum”, or “what's in Europe”.",
            docs[:6],
        )

    return None


def recommend_intent(index: PlaceIndex, question: str):
    """There is no rating in the data, so say so — then be useful anyway."""
    if not re.search(
        r"\bbest\b|\brecommend\b|\bsuggest\b|\bworth (?:seeing|visiting|a visit)\b"
        r"|\bshould i (?:see|visit|go)\b|\btop \d*\s*place|\bmust[- ]see\b|\bfavou?rite\b",
        question,
        re.I,
    ):
        return None

    lowered = question.lower()
    pool = index.documents
    scope = "the atlas"
    if "india" in lowered:
        pool = [d for d in index.documents if d.atlas == "india"]
        scope = "the India atlas"
    elif "world" in lowered:
        pool = [d for d in index.documents if d.atlas == "world"]
        scope = "the world atlas"

    # One per category, so the sample spans the map rather than clustering.
    picked: list[Document] = []
    for category in sorted({doc.place.category for doc in pool}):
        picked.append(next(doc for doc in pool if doc.place.category == category))

    return (
        "These records don't carry ratings, so I can't rank them honestly — nothing in the "
        f"data says which is 'best'. What I can do is show you the spread of {scope}, one "
        "from each region:\n\n"
        + "\n".join(f"· {doc.place.title} — {doc.place.category}" for doc in picked[:6])
        + "\n\nAsk about any of them by name for the full record.",
        picked[:6],
    )


def help_intent(index: PlaceIndex, question: str):
    """Nothing to search on — explain what this thing actually does."""
    from src.guide.text import tokenise

    if tokenise(question):
        return None

    return (
        f"I answer from the {len(index.documents)} records plotted on these maps — nothing "
        "else. You can ask me to:\n\n"
        "· describe a place — “Ladakh”, “the Taj Mahal”\n"
        "· count or list — “what's in South India”, “how many landmarks”\n"
        "· measure — “how far is the Eiffel Tower from the Colosseum”\n"
        "· locate — “where is Machu Picchu”, “what's nearest to Goa”\n"
        "· compare — “compare Stonehenge and the Great Wall”",
        [],
    )


HANDLERS = (
    help_intent,
    recommend_intent,
    compare_intent,
    count_intent,
    nearest_intent,
    superlative_intent,
    overview_intent,
    where_intent,
    list_intent,
)


def resolve(index: PlaceIndex, question: str):
    for handler in HANDLERS:
        result = handler(index, question)
        if result:
            return result
    return None

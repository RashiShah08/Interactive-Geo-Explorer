"""A small TF-IDF vector-space index over the place records."""
import math
from collections import Counter
from dataclasses import dataclass, field

from src.data.india_states import INDIA_STATES
from src.data.models import GeoPlace
from src.data.world_landmarks import WORLD_LANDMARKS
from src.guide.text import tokenise

# The title is short but far more identifying than the prose, so it counts for more.
TITLE_WEIGHT = 4
CATEGORY_WEIGHT = 2


@dataclass
class Document:
    place: GeoPlace
    atlas: str
    vector: dict[str, float] = field(default_factory=dict)
    norm: float = 0.0
    title_tokens: frozenset[str] = frozenset()


@dataclass
class Hit:
    document: Document
    score: float
    coverage: float
    named: bool             # the question used a word from this record's title
    unmatched: frozenset[str] = frozenset()  # asked-for terms this record lacks

    @property
    def is_lookup(self) -> bool:
        """The question named this record and asked nothing else of it.

        'tell me something about Ladakh' qualifies once filler is stripped;
        'the capital of France' does not, because 'capital' goes unanswered.
        """
        return self.named and not self.unmatched

    def __iter__(self):
        """Unpack as (document, score, coverage)."""
        return iter((self.document, self.score, self.coverage))


class PlaceIndex:
    def __init__(self, entries: list[tuple[GeoPlace, str]]):
        self.documents = [Document(place=place, atlas=atlas) for place, atlas in entries]
        self._build()

    def _terms(self, place: GeoPlace) -> list[str]:
        return (
            tokenise(place.title) * TITLE_WEIGHT
            + tokenise(place.category) * CATEGORY_WEIGHT
            + tokenise(place.description)
        )

    def _build(self) -> None:
        counts = [Counter(self._terms(doc.place)) for doc in self.documents]

        document_frequency: Counter[str] = Counter()
        for count in counts:
            document_frequency.update(count.keys())

        total = len(self.documents)
        self.idf = {
            term: math.log((total + 1) / (freq + 1)) + 1
            for term, freq in document_frequency.items()
        }

        for doc, count in zip(self.documents, counts):
            longest = max(count.values())
            doc.vector = {
                term: (0.5 + 0.5 * freq / longest) * self.idf[term]
                for term, freq in count.items()
            }
            doc.norm = math.sqrt(sum(weight * weight for weight in doc.vector.values())) or 1.0
            doc.title_tokens = frozenset(tokenise(doc.place.title))

    def search(self, query: str, limit: int = 5) -> list[Hit]:
        """Rank records against a question.

        `coverage` is the share of the question's distinctive weight that the
        document accounts for; unseen words count against it, which is what stops
        "the capital of France" being answered with the Eiffel Tower entry. An
        unseen word is charged the *median* weight rather than the maximum,
        because most of them are conversational filler rather than real demands.
        """
        tokens = tokenise(query)
        if not tokens:
            return []

        known = sorted(self.idf.values())
        unknown_idf = known[len(known) // 2] if known else 1.0
        counts = Counter(tokens)
        longest = max(counts.values())
        query_vector = {
            term: (0.5 + 0.5 * freq / longest) * self.idf.get(term, 0.0)
            for term, freq in counts.items()
        }
        query_norm = math.sqrt(sum(w * w for w in query_vector.values())) or 1.0

        demand = {term: self.idf.get(term, unknown_idf) for term in counts}
        total_demand = sum(demand.values()) or 1.0

        scored = []
        query_tokens = set(tokens)
        for doc in self.documents:
            overlap = query_vector.keys() & doc.vector.keys()
            if not overlap:
                continue

            dot = sum(query_vector[term] * doc.vector[term] for term in overlap)
            score = dot / (query_norm * doc.norm)

            # Reward answering the distinctive parts of the question, not just
            # sharing common words with it.
            coverage = sum(demand[term] for term in overlap) / total_demand
            score += 0.35 * coverage

            # A query that names the place outright should win regardless of prose overlap.
            matched_title = query_tokens & doc.title_tokens
            if matched_title:
                score += 0.35 * len(matched_title) / len(doc.title_tokens)

            if score > 0:
                scored.append(
                    Hit(
                        document=doc,
                        score=score,
                        coverage=coverage,
                        named=bool(matched_title),
                        unmatched=frozenset(counts) - overlap,
                    )
                )

        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[:limit]

    def by_category(self, needle: str) -> list[Document]:
        needle = needle.lower().strip()
        return [doc for doc in self.documents if needle in doc.place.category.lower()]

    def categories(self) -> list[str]:
        return sorted({doc.place.category for doc in self.documents})


def build_index() -> PlaceIndex:
    return PlaceIndex(
        [(place, "world") for place in WORLD_LANDMARKS]
        + [(place, "india") for place in INDIA_STATES]
    )


INDEX = build_index()

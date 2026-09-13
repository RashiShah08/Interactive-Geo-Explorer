"""Composes a reply from the corpus. Everything returned is either quoted from a
record or computed from one, and each reply names the records it drew on."""
from dataclasses import dataclass

from src.guide import intents
from src.guide.index import INDEX, Document, PlaceIndex
from src.guide.text import sentences, tokenise

STRONG = 0.34       # confident enough to answer outright
WEAK = 0.12         # worth offering as a suggestion, not as an answer
MIN_COVERAGE = 0.55 # the reply must address most of what was actually asked


@dataclass
class Reply:
    text: str
    citations: list[dict]


def _cite(doc: Document) -> dict:
    return {
        "key": doc.place.key,
        "title": doc.place.title,
        "atlas": doc.atlas,
        "category": doc.place.category,
    }


def _relevant_extract(text: str, question: str, limit: int = 3) -> str:
    """Pull the sentences that actually address the question, in original order."""
    query = set(tokenise(question))
    parts = sentences(text)
    if len(parts) <= limit or not query:
        return text

    scored = []
    for position, sentence in enumerate(parts):
        overlap = len(query & set(tokenise(sentence)))
        scored.append((overlap, position, sentence))

    best = sorted(scored, key=lambda row: (-row[0], row[1]))[:limit]
    if not any(row[0] for row in best):
        return " ".join(parts[:limit])
    return " ".join(sentence for _, _, sentence in sorted(best, key=lambda row: row[1]))


def _describe(doc: Document, question: str) -> str:
    place = doc.place
    return (
        f"{place.title} — {place.category}.\n\n"
        f"{_relevant_extract(place.description, question)}"
    )


def answer(question: str, index: PlaceIndex | None = None) -> Reply:
    index = index or INDEX
    question = (question or "").strip()

    if not question:
        return Reply("Ask me about any of the 47 places in the atlas.", [])

    # 1. Questions that are arithmetic over the corpus rather than a lookup.
    structured = intents.resolve(index, question)
    if structured:
        text, docs = structured
        return Reply(text, [_cite(doc) for doc in docs])

    # 2. Otherwise fall back to retrieval over the descriptions.
    hits = index.search(question, limit=4)
    if not hits:
        return Reply(
            "Nothing in the atlas matches that. I only know the 47 records plotted here — "
            "try a place name, a category like “South India” or “Europe”, or ask how far "
            "two of them are apart.",
            [],
        )

    top = hits[0]
    top_doc = top.document

    # Naming a record and asking nothing further is a lookup, not a research
    # question: answer it even if the sentence was mostly conversational padding.
    confident = top.is_lookup or (top.score >= STRONG and top.coverage >= MIN_COVERAGE)

    if confident and top.score >= WEAK:
        others = [hit.document for hit in hits[1:] if hit.score >= STRONG * 0.8][:2]
        text = _describe(top_doc, question)
        if others:
            text += "\n\nAlso related: " + ", ".join(doc.place.title for doc in others) + "."
        return Reply(text, [_cite(doc) for doc in [top_doc, *others]])

    if top.score >= WEAK:
        names = [hit.document.place.title for hit in hits[:3]]
        lead = (
            "I only hold what's written on these records, and that question goes past them."
            if top.coverage < MIN_COVERAGE
            else "I'm not certain what you're after."
        )
        return Reply(
            f"{lead} The closest entries are "
            + ", ".join(names)
            + ". Ask about one by name and I'll give you its full record.",
            [_cite(hit.document) for hit in hits[:3]],
        )

    return Reply(
        "That doesn't match anything in the atlas closely enough to answer honestly. "
        "I can only speak to the 47 records plotted here.",
        [],
    )

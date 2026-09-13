"""Tokenising and light stemming. Pure standard library on purpose — the whole
point of this guide is that it has no external dependencies to rot."""
import re

STOPWORDS = frozenset(
    """
    a an the and or but if of in on at to from by for with about into over after
    is are was were be been being am do does did doing have has had having
    i me my we our you your he she it its they them their this that these those
    what which who whom whose when where why how there here
    can could should would will shall may might must
    as than then so such just very much many more most some any all both each
    tell show give find know like want need please thanks thank hi hello hey
    something anything everything nothing someone anyone somewhere anywhere
    info information detail details thing things stuff bit lot little
    also again really actually maybe perhaps quite rather pretty
    """.split()
)

# Stemmed forms of the above, since filler is stripped after normalising too.
STOPSTEMS = frozenset({"someth", "anyth", "everyth", "noth", "detail", "thing"})

# Suffix trimming only — enough to match "temples"/"temple" without a stemmer library.
# Verb/adjective endings are stripped before the plural "s", otherwise "temples"
# loses its "es" and stops matching "temple".
_SUFFIXES = ("ing", "est", "ers", "ed", "er", "ly")

_WORD = re.compile(r"[a-z0-9]+")


def normalise(word: str) -> str:
    word = word.lower()
    if len(word) <= 4:
        return word

    if word.endswith("ies"):
        return word[:-3] + "y"

    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]

    if word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]

    return word


def tokenise(text: str, *, keep_stopwords: bool = False) -> list[str]:
    words = _WORD.findall(text.lower())
    if keep_stopwords:
        return [normalise(word) for word in words]

    tokens = []
    for word in words:
        if word in STOPWORDS or len(word) <= 1:
            continue
        stem = normalise(word)
        if stem in STOPSTEMS:
            continue
        tokens.append(stem)
    return tokens


def sentences(text: str) -> list[str]:
    """Split prose into sentences without over-splitting on '8,848.86 m' or 'H.No:'."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", text.strip())
    return [part.strip() for part in parts if part.strip()]

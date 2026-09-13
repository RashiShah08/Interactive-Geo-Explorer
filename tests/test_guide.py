"""The guide must answer from the corpus or admit it cannot. These tests pin
both halves of that bargain."""
import pytest

from src.guide.answer import answer
from src.guide.index import INDEX
from src.guide.intents import haversine_km
from src.guide.text import normalise, sentences, tokenise


# ------------------------------------------------------------- text handling

def test_tokenise_drops_stopwords_and_stems():
    tokens = tokenise("Tell me about the temples of Kyoto")
    assert "the" not in tokens and "about" not in tokens
    assert "temple" in tokens
    assert "kyoto" in tokens


@pytest.mark.parametrize(
    ("word", "expected"),
    [("temples", "temple"), ("tallest", "tall"), ("cities", "city"), ("lead", "lead")],
)
def test_normalise(word, expected):
    assert normalise(word) == expected


def test_sentences_do_not_split_on_decimals():
    text = "It rises 8,848.86 m above sea level. Climbers come every year."
    assert len(sentences(text)) == 2


# ----------------------------------------------------------------- retrieval

def test_index_covers_every_record():
    assert len(INDEX.documents) == 47
    assert sum(d.atlas == "world" for d in INDEX.documents) == 18
    assert sum(d.atlas == "india" for d in INDEX.documents) == 29


@pytest.mark.parametrize(
    ("question", "expected_title"),
    [
        ("tell me about Kerala", "Kerala"),
        ("what is the taj mahal", "Taj Mahal (India)"),
        ("the tallest sandcastle", "Odisha"),
        ("bridge made of popsicle sticks", "Jharkhand"),
        ("highest altitude piano performance", "Ladakh"),
        ("reciting the periodic table", "Haryana"),
    ],
)
def test_retrieval_finds_the_right_record(question, expected_title):
    reply = answer(question)
    assert reply.citations, f"no citation for {question!r}"
    assert reply.citations[0]["title"] == expected_title


def test_answers_are_grounded_in_the_cited_record():
    reply = answer("tell me about the tallest sandcastle")
    place = next(d.place for d in INDEX.documents if d.place.key == reply.citations[0]["key"])
    # Every sentence of the reply body must come from that record's own text.
    body = reply.text.split("\n\n", 1)[1]
    for sentence in sentences(body):
        assert sentence in place.description


# ------------------------------------------------------------------ refusals

@pytest.mark.parametrize(
    "question",
    ["what is the capital of France", "what's the population of India", "who won the world cup"],
)
def test_declines_questions_the_corpus_cannot_answer(question):
    reply = answer(question)
    assert "goes past them" in reply.text or "doesn't match anything" in reply.text


def test_empty_question_is_handled():
    assert answer("").citations == []


# ------------------------------------------------- conversational phrasing
# Regression guards: filler words around a place name once dropped coverage
# below threshold, so "tell me something about Ladakh" was refused while the
# bare word "Ladakh" worked.

@pytest.mark.parametrize(
    "question",
    [
        "ladakh",
        "tell me something about ladakh",
        "tell me a bit about ladakh please",
        "i want to know more about ladakh",
        "what about ladakh",
    ],
)
def test_filler_words_do_not_block_a_named_place(question):
    reply = answer(question)
    assert reply.text.startswith("Ladakh —"), reply.text[:80]


def test_naming_a_place_still_does_not_answer_unrelated_questions():
    """'France' appears in a title, but 'capital' is not something we hold."""
    reply = answer("what is the capital of France")
    assert "goes past them" in reply.text


# ----------------------------------------------------------------- overviews

def test_asking_about_india_describes_the_atlas():
    reply = answer("tell me something about india")
    assert "29 states" in reply.text
    assert "North India (9)" in reply.text


def test_asking_about_the_world_describes_the_atlas():
    assert "18 landmarks" in answer("tell me about the world").text


def test_recommendations_admit_there_is_no_ranking():
    reply = answer("best places to visit")
    assert "can't rank them" in reply.text
    assert len(reply.citations) >= 3


def test_recommendations_can_be_scoped_to_india():
    reply = answer("what should i visit in india")
    assert "India atlas" in reply.text
    assert all("India" in c["category"] for c in reply.citations)


def test_capability_question_explains_what_it_does():
    reply = answer("what can you do")
    assert "47 records" in reply.text


# -------------------------------------------------------------- computed answers

def test_counts_by_category():
    reply = answer("how many places are in South India?")
    assert "5" in reply.text
    assert len(reply.citations) == 5


def test_total_count():
    assert "29" in answer("how many states are in the india atlas?").text


def test_distance_between_two_places():
    reply = answer("how far is the Eiffel Tower from the Colosseum?")
    assert "km apart" in reply.text
    assert {c["title"] for c in reply.citations} == {"Eiffel Tower (France)", "Colosseum (Italy)"}


def test_distance_matches_haversine():
    paris = next(d.place for d in INDEX.documents if d.place.key == "eiffel_tower")
    rome = next(d.place for d in INDEX.documents if d.place.key == "colosseum")
    assert 1050 < haversine_km(paris, rome) < 1150


def test_nearest_returns_ordered_neighbours():
    reply = answer("what is nearest to Goa")
    assert reply.citations[0]["title"] == "Goa"
    assert reply.citations[1]["title"] == "Karnataka"


def test_northernmost_in_india():
    assert "Ladakh" in answer("which is the northernmost place in india").text


def test_listing_a_category():
    reply = answer("list everything in Northeast India")
    assert len(reply.citations) == 6
    assert "Meghalaya" in reply.text


def test_compare_two_places():
    reply = answer("compare Stonehenge and the Great Wall")
    assert "km apart" in reply.text
    assert len(reply.citations) == 2

import os, tempfile, json
from scripts import rag_ingest

def test_score_chunk_for_clarification_basic():
    # High ambiguity: early pronouns, acronyms, entities, length
    txt = "This system uses TBD metrics. It integrates CPU GPU RAM and IO subsystems for ACME Quantum Processing." * 3
    score = rag_ingest._score_chunk_for_clarification(txt)  # type: ignore
    assert 3 <= score <= 9

    short_txt = "Simple note."  # minimal signals
    low_score = rag_ingest._score_chunk_for_clarification(short_txt)  # type: ignore
    assert 1 <= low_score <= score


def test_simple_clarifying_generation():
    qs = rag_ingest._simple_clarifying_questions("Alpha Beta Gamma Delta", 3)  # type: ignore
    assert len(qs) == 3
    assert any("Alpha" in q for q in qs)

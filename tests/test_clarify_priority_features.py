from app.rag.clarify_priority_features import extract_features


def test_extract_features_basic():
    text = "This system processes CPU and GPU tasks. It handles IO TBD later. ACME ENGINE v2 processes 32ms frames." * 2
    feats, meta = extract_features(text)
    # Sanity: mandatory keys
    for k in [
        "char_len","word_len","sentence_count","avg_sentence_len","pronoun_early_count",
        "acronym_count","capitalized_entity_count","numeric_unit_count","todo_marker",
        "log_char_len","log_word_len"
    ]:
        assert k in feats
    assert feats["char_len"] > 0
    assert meta["version"] == 0

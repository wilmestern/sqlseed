"""Tests for sqlseed.row_annotator."""
import pytest

from sqlseed.row_annotator import AnnotatorConfig, AnnotatorError, RowAnnotator


# ---------------------------------------------------------------------------
# AnnotatorConfig
# ---------------------------------------------------------------------------

def test_annotator_config_defaults():
    cfg = AnnotatorConfig()
    assert cfg.prefix == "__"
    assert cfg.suffix == "__"
    assert cfg.overwrite is False


def test_annotator_config_annotation_key():
    cfg = AnnotatorConfig(prefix="_", suffix="_")
    assert cfg.annotation_key("meta") == "_meta_"


def test_annotator_config_empty_prefix_and_suffix_raises():
    with pytest.raises(AnnotatorError):
        AnnotatorConfig(prefix="", suffix="")


def test_annotator_config_empty_prefix_only_is_valid():
    cfg = AnnotatorConfig(prefix="", suffix="_end")
    assert cfg.annotation_key("tag") == "tag_end"


# ---------------------------------------------------------------------------
# RowAnnotator.add / remove / clear / names
# ---------------------------------------------------------------------------

def test_add_registers_annotation():
    ann = RowAnnotator()
    ann.add("seq", lambda row: 1)
    assert "seq" in ann.names()


def test_add_non_callable_raises():
    ann = RowAnnotator()
    with pytest.raises(AnnotatorError):
        ann.add("bad", "not_a_function")  # type: ignore[arg-type]


def test_add_empty_name_raises():
    ann = RowAnnotator()
    with pytest.raises(AnnotatorError):
        ann.add("", lambda row: None)


def test_remove_existing():
    ann = RowAnnotator()
    ann.add("tag", lambda row: "x")
    ann.remove("tag")
    assert "tag" not in ann.names()


def test_remove_unknown_does_not_raise():
    ann = RowAnnotator()
    ann.remove("nonexistent")  # should not raise


def test_clear_removes_all():
    ann = RowAnnotator()
    ann.add("a", lambda row: 1)
    ann.add("b", lambda row: 2)
    ann.clear()
    assert ann.names() == []


# ---------------------------------------------------------------------------
# RowAnnotator.annotate
# ---------------------------------------------------------------------------

def test_annotate_returns_new_dict():
    ann = RowAnnotator()
    row = {"id": 1}
    result = ann.annotate(row)
    assert result is not row


def test_annotate_preserves_original_columns():
    ann = RowAnnotator()
    ann.add("ts", lambda row: "2024-01-01")
    row = {"id": 5, "name": "alice"}
    result = ann.annotate(row)
    assert result["id"] == 5
    assert result["name"] == "alice"


def test_annotate_adds_annotation_key():
    ann = RowAnnotator()
    ann.add("source", lambda row: "generated")
    result = ann.annotate({"id": 1})
    assert result["__source__"] == "generated"


def test_annotate_fn_receives_original_row():
    ann = RowAnnotator()
    ann.add("double_id", lambda row: row["id"] * 2)
    result = ann.annotate({"id": 7})
    assert result["__double_id__"] == 14


def test_annotate_collision_raises_when_overwrite_false():
    cfg = AnnotatorConfig(overwrite=False)
    ann = RowAnnotator(config=cfg)
    ann.add("id", lambda row: 99)
    row = {"__id__": "existing"}
    with pytest.raises(AnnotatorError):
        ann.annotate(row)


def test_annotate_collision_allowed_when_overwrite_true():
    cfg = AnnotatorConfig(overwrite=True)
    ann = RowAnnotator(config=cfg)
    ann.add("id", lambda row: 99)
    row = {"__id__": "existing"}
    result = ann.annotate(row)
    assert result["__id__"] == 99


def test_annotate_rows_returns_list_of_same_length():
    ann = RowAnnotator()
    ann.add("flag", lambda row: True)
    rows = [{"id": i} for i in range(5)]
    results = ann.annotate_rows(rows)
    assert len(results) == 5


def test_annotate_rows_each_row_has_annotation():
    ann = RowAnnotator()
    ann.add("flag", lambda row: True)
    rows = [{"id": i} for i in range(3)]
    results = ann.annotate_rows(rows)
    assert all(r["__flag__"] is True for r in results)

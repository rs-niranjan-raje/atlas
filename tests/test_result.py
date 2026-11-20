import pytest
from pydantic import ValidationError

from atlas.schemas.document import Document
from atlas.schemas.result import SearchResult


def test_valid_result():

    doc = Document(id="123", title="Test Document", text="This is a test document.")
    result = SearchResult(document=doc, score=0.85)

    assert result.document.id == "123"
    assert result.document.title == "Test Document"
    assert result.score == 0.85


def test_score_above_one_is_rejected():
    doc = Document(id="123", title="T", text="x")
    with pytest.raises(ValidationError):
        SearchResult(document=doc, score=1.5)


def test_score_below_zero_is_rejected():
    doc = Document(id="123", title="T", text="x")
    with pytest.raises(ValidationError):
        SearchResult(document=doc, score=-0.1)


def test_score_edge_case_zero():
    doc = Document(id="123", title="T", text="x")
    result = SearchResult(document=doc, score=0.0)
    assert result.score == 0.0


def test_score_edge_case_one():
    doc = Document(id="123", title="T", text="x")
    result = SearchResult(document=doc, score=1.0)
    assert result.score == 1.0

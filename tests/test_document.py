import pytest
from pydantic import ValidationError

from atlas.schemas.document import Document


def test_valid_document():
    doc = Document(id="d1", title="Hello", text="Some text", url="https://example.com")
    assert doc.title == "Hello"


def test_url_is_optional():
    assert Document(id="d1", title="Hello", text="x").url is None


def test_empty_title_is_rejected():
    with pytest.raises(ValidationError):
        Document(id="d1", title="", text="x")


def test_bad_url_is_rejected():
    with pytest.raises(ValidationError):
        Document(id="d1", title="Hello", text="x", url="not a url")

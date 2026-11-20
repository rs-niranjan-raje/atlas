import pytest
from pydantic import ValidationError

from atlas.schemas.search import SearchQuery


def test_valid_query_has_default_max_results():
    q = SearchQuery(text="python async")
    assert q.max_results == 5


def test_empty_text_is_rejected():
    with pytest.raises(ValidationError):
        SearchQuery(text="")


def test_zero_max_results_is_rejected():
    with pytest.raises(ValidationError):
        SearchQuery(text="python", max_results=0)


def test_blank_text_is_rejected():
    with pytest.raises(ValidationError):
        SearchQuery(text=" ")

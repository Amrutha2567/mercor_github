import pytest
from app.github_client import username_from_url

def test_extract_username():
    assert username_from_url("https://github.com/octocat") == "octocat"

def test_reject_non_profile_url():
    with pytest.raises(ValueError):
        username_from_url("https://github.com/octocat/repo")

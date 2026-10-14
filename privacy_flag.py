"""If a listing's image_tags ever include a person/face/child tag, it needs
a privacy review before anything downstream (insights, search, generation)
touches it. None of the four teaching SKUs trigger this; the function
exists so a real catalog import can't silently skip the check.
"""
SENSITIVE = {"person", "face", "child"}


def needs_privacy_review(tags) -> bool:
    return any(t in SENSITIVE for t in (tags or []))


if __name__ == "__main__":
    assert needs_privacy_review(["kiondo"]) is False
    assert needs_privacy_review(["bag", "person"]) is True
    print("privacy flag OK")

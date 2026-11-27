"""Reserved listings: flagged, hidden by default, and pagination still follows the API page.

Run: python tests/test_reserved.py
"""

from marktplaats_mcp import server


def _listing(item_id: str, reserved: bool) -> dict:
    return {
        "itemId": item_id,
        "title": item_id,
        "priceInfo": {"priceType": "MIN_BID", "priceCents": 10000},
        "reserved": reserved,
    }


class _FakeResponse:
    def __init__(self, data: dict):
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _search(**kwargs) -> dict:
    page = {"totalResultCount": 10, "listings": [_listing("m1", False), _listing("m2", True)]}
    server._get_request = lambda *args, **kw: _FakeResponse(page)
    return server.search_listings(query="x", limit=2, **kwargs)


def main() -> None:
    assert server._is_reserved(_listing("m1", True))
    assert not server._is_reserved(_listing("m1", False))
    assert server._is_reserved({"priceInfo": {"priceType": "RESERVED"}})

    hidden = _search()
    assert [item["id"] for item in hidden["listings"]] == ["m1"]
    assert hidden["next_offset"] == 2, "next page starts after the whole API page"

    shown = _search(exclude_reserved=False)
    assert [item["reserved"] for item in shown["listings"]] == [False, True]

    compact = _search(exclude_reserved=False, compact=True)
    assert "reserved" not in compact["listings"][0]
    assert compact["listings"][1]["reserved"] is True
    assert compact["next"] == 2

    print("ok")


if __name__ == "__main__":
    main()

"""Site selection: 2dehands uses its own domain end to end, unknown sites never reach a URL.

Run: python tests/test_sites.py
"""

from marktplaats_mcp import server


class _FakeResponse:
    def __init__(self, data: dict):
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def main() -> None:
    called = []

    def fake_get(url, *args, **kwargs):
        called.append(url)
        page = {"totalResultCount": 1, "listings": [
            {"itemId": "m1", "title": "x", "priceInfo": {"priceType": "FIXED", "priceCents": 100}}
        ]}
        return _FakeResponse(page)

    server._get_request = fake_get

    result = server.search_listings(query="x", site="2dehands")
    assert called == ["https://www.2dehands.be/lrp/api/search"], called
    assert result["listings"][0]["link"] == "https://link.2dehands.be/m1"

    called.clear()
    default = server.search_listings(query="x")
    assert called == ["https://www.marktplaats.nl/lrp/api/search"], called
    assert default["listings"][0]["link"] == "https://link.marktplaats.nl/m1"

    called.clear()
    for tool, args in (
        (server.search_listings, {"query": "x"}),
        (server.get_listing_details, {"listing_id": "m1"}),
        (server.get_seller_info, {"seller_id": 1}),
        (server.get_category_filters, {"category": "computers en software"}),
    ):
        assert "error" in tool(**args, site="example.com"), tool.__name__
    assert called == [], "an unknown site reached a request"

    print("ok")


if __name__ == "__main__":
    main()

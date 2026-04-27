from dataclasses import dataclass
from typing import NamedTuple


class CrawlTarget(NamedTuple):
    domain: str
    base_url: str
    rate_limit_per_minute: int
    requires_js: bool
    search_endpoint: str | None = None


CRAWL_TARGETS = [
    CrawlTarget(
        domain="google.com",
        base_url="https://www.google.com",
        rate_limit_per_minute=10,
        requires_js=False,
        search_endpoint="/search?q={query}&tbm=isch",
    ),
    CrawlTarget(
        domain="twitter.com",
        base_url="https://twitter.com",
        rate_limit_per_minute=20,
        requires_js=True,
        search_endpoint="/search?q={query}",
    ),
    CrawlTarget(
        domain="x.com",
        base_url="https://x.com",
        rate_limit_per_minute=20,
        requires_js=True,
        search_endpoint="/search?q={query}",
    ),
    CrawlTarget(
        domain="reddit.com",
        base_url="https://www.reddit.com",
        rate_limit_per_minute=15,
        requires_js=False,
        search_endpoint="/search?q={query}",
    ),
    CrawlTarget(
        domain="instagram.com",
        base_url="https://www.instagram.com",
        rate_limit_per_minute=15,
        requires_js=True,
        search_endpoint="/explore/search/?search_term={query}",
    ),
    CrawlTarget(
        domain="tiktok.com",
        base_url="https://www.tiktok.com",
        rate_limit_per_minute=15,
        requires_js=True,
        search_endpoint="/api/search/general/full/?keyword={query}",
    ),
    CrawlTarget(
        domain="facebook.com",
        base_url="https://www.facebook.com",
        rate_limit_per_minute=10,
        requires_js=True,
        search_endpoint="/search/top/?q={query}",
    ),
    CrawlTarget(
        domain="youtube.com",
        base_url="https://www.youtube.com",
        rate_limit_per_minute=15,
        requires_js=False,
        search_endpoint="/results?search_query={query}",
    ),
    CrawlTarget(
        domain="imgur.com",
        base_url="https://imgur.com",
        rate_limit_per_minute=20,
        requires_js=False,
        search_endpoint="/search/{query}",
    ),
    CrawlTarget(
        domain="flickr.com",
        base_url="https://www.flickr.com",
        rate_limit_per_minute=15,
        requires_js=False,
        search_endpoint="/search/all/?text={query}",
    ),
]

CRAWL_TARGETS_BY_DOMAIN = {t.domain: t for t in CRAWL_TARGETS}


def get_target(domain: str) -> CrawlTarget | None:
    return CRAWL_TARGETS_BY_DOMAIN.get(domain)
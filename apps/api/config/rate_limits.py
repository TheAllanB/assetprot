# Requests per window per org per endpoint
RATE_LIMIT_REQUESTS: int = 100
RATE_LIMIT_WINDOW_SECONDS: int = 60

# Crawler: requests per domain per minute (prevents GUARDIAN becoming a DDoS tool)
CRAWLER_RATE_LIMIT_REQUESTS: int = 10
CRAWLER_RATE_LIMIT_WINDOW_SECONDS: int = 60

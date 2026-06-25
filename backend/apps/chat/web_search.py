import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class WebResult:
    title: str
    url: str
    content: str
    position: int


def search_web(query: str, max_results: int | None = None) -> list[WebResult]:
    api_key = os.getenv('TAVILY_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('TAVILY_API_KEY 未配置')

    limit = max_results or int(os.getenv('TAVILY_MAX_RESULTS', '5'))
    search_depth = os.getenv('TAVILY_SEARCH_DEPTH', 'basic')

    response = requests.post(
        'https://api.tavily.com/search',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'query': query,
            'search_depth': search_depth,
            'max_results': limit,
            'include_answer': False,
            'include_raw_content': False,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    results: list[WebResult] = []
    for index, item in enumerate(data.get('results', []), start=1):
        title = (item.get('title') or '').strip()
        url = (item.get('url') or '').strip()
        content = (item.get('content') or '').strip()
        if not url or not content:
            continue
        results.append(
            WebResult(
                title=title or url,
                url=url,
                content=content[:800],
                position=index,
            )
        )
    return results

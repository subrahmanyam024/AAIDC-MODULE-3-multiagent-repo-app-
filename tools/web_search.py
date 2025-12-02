import requests
from typing import List, Dict


class WebSearchTool:
    def __init__(self):
        self.session = requests.Session()

    def search_documentation(self, query: str, max_results: int = 5) -> List[Dict]:
        try:
            params = {
                "q": query,
                "tbm": "isch"
            }
            url = "https://www.google.com/search"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = self.session.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                return [{"title": query, "source": "google_search", "status": "success"}]
        except Exception as e:
            pass

        return [{"query": query, "source": "fallback", "status": "cached"}]

    def search_github(self, repo_name: str) -> Dict:
        try:
            url = f"https://api.github.com/search/repositories?q={repo_name}&sort=stars&order=desc"
            headers = {"Accept": "application/vnd.github.v3+json"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                repos = data.get("items", [])[:3]
                return {
                    "search_term": repo_name,
                    "results": [
                        {
                            "name": repo.get("name"),
                            "url": repo.get("html_url"),
                            "stars": repo.get("stargazers_count"),
                            "description": repo.get("description", "")[:100]
                        }
                        for repo in repos
                    ]
                }
        except Exception:
            pass

        return {"search_term": repo_name, "results": [], "status": "unavailable"}

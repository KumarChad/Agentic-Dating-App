import httpx

def test_ddg_api(query: str):
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            res = client.get(url)
            data = res.json()
            return {
                "Heading": data.get("Heading"),
                "Abstract": data.get("Abstract"),
                "AbstractText": data.get("AbstractText"),
                "Results": data.get("Results")
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Testing DDG API for Satya Nadella:")
    print(test_ddg_api("Satya Nadella Microsoft LinkedIn"))

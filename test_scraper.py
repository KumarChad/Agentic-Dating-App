import re
import urllib.parse
import httpx
from bs4 import BeautifulSoup

def scrape_linkedin(linkedin_url: str):
    slug = linkedin_url.strip().rstrip('/').split('/')[-1]
    if '?' in slug:
        slug = slug.split('?')[0]
    
    # Clean slug format (e.g. satya-nadella -> Satya Nadella)
    clean_name = slug.replace('-', ' ').title()

    # Query public search engines for the indexed snippet
    queries = [
        f"https://html.duckduckgo.com/html/?q={urllib.parse.quote('site:linkedin.com/in/' + slug)}",
        f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(clean_name + ' LinkedIn profile overview')}"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    scraped_data = {
        "platform": "LinkedIn",
        "url": linkedin_url,
        "slug": slug,
        "name": clean_name,
        "headline": "",
        "summary": ""
    }

    with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
        for q_url in queries:
            try:
                res = client.get(q_url)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    snippets = soup.find_all("a", class_="result__snippet")
                    titles = soup.find_all("a", class_="result__title")

                    for t, s in zip(titles, snippets):
                        t_text = t.get_text(strip=True)
                        s_text = s.get_text(strip=True)
                        if slug.lower() in t.get("href", "").lower() or clean_name.lower() in t_text.lower():
                            scraped_data["headline"] = t_text
                            scraped_data["summary"] = s_text
                            return scraped_data
            except Exception as e:
                pass

    return scraped_data

def scrape_instagram(instagram_url: str):
    handle = instagram_url.strip().rstrip('/').split('/')[-1]
    if '?' in handle:
        handle = handle.split('?')[0]

    q_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote('site:instagram.com/' + handle)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    scraped_data = {
        "platform": "Instagram",
        "url": instagram_url,
        "handle": handle,
        "bio": "",
        "posts_summary": ""
    }

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            res = client.get(q_url)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                snippet = soup.find("a", class_="result__snippet")
                title = soup.find("a", class_="result__title")

                if snippet:
                    scraped_data["bio"] = snippet.get_text(strip=True)
                if title:
                    scraped_data["posts_summary"] = title.get_text(strip=True)
    except Exception as e:
        pass

    return scraped_data

if __name__ == "__main__":
    print("=== Testing Scraper on Real Accounts ===")
    print("LinkedIn (Satya Nadella):", scrape_linkedin("https://www.linkedin.com/in/satyanadella"))
    print("Instagram (Satya Nadella):", scrape_instagram("https://www.instagram.com/satyanadella/"))

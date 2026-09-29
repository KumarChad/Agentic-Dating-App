import re
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any

class RealScraper:
    """
    Scrapes public metadata from LinkedIn and Instagram profiles.
    Extracts OpenGraph titles, descriptions, bios, headlines, and keywords.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    @classmethod
    def scrape_linkedin(cls, linkedin_url: str) -> Dict[str, str]:
        clean_url = linkedin_url.strip()
        slug = clean_url.rstrip('/').split('/')[-1].split('?')[0]
        fallback_name = slug.replace('-', ' ').title()

        data = {
            "platform": "LinkedIn",
            "url": clean_url,
            "slug": slug,
            "name": fallback_name,
            "headline": "Professional & Builder",
            "description": f"Public profile for {fallback_name} on LinkedIn.",
            "raw_text": ""
        }

        try:
            with httpx.Client(timeout=8.0, follow_redirects=True, headers=cls.HEADERS) as client:
                res = client.get(clean_url)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    og_title = soup.find("meta", property="og:title")
                    og_desc = soup.find("meta", property="og:description")
                    title_tag = soup.find("title")

                    if og_title and og_title.get("content"):
                        title_val = og_title["content"]
                        if "-" in title_val:
                            data["name"] = title_val.split("-")[0].strip()
                            data["headline"] = title_val.split("-", 1)[1].replace("| LinkedIn", "").strip()
                        else:
                            data["name"] = title_val

                    elif title_tag and title_tag.string:
                        t_val = title_tag.string
                        if "-" in t_val:
                            data["name"] = t_val.split("-")[0].strip()

                    if og_desc and og_desc.get("content"):
                        data["description"] = og_desc["content"]

                    data["raw_text"] = soup.get_text(separator=" ", strip=True)[:1500]
        except Exception as e:
            pass

        return data

    @classmethod
    def scrape_instagram(cls, instagram_url: str) -> Dict[str, str]:
        clean_url = instagram_url.strip()
        handle = clean_url.rstrip('/').split('/')[-1].split('?')[0]

        data = {
            "platform": "Instagram",
            "url": clean_url,
            "handle": handle,
            "name": handle.capitalize(),
            "bio": f"Public Instagram profile @{handle}",
            "raw_text": ""
        }

        try:
            with httpx.Client(timeout=8.0, follow_redirects=True, headers=cls.HEADERS) as client:
                res = client.get(clean_url)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    og_title = soup.find("meta", property="og:title")
                    og_desc = soup.find("meta", property="og:description")

                    if og_title and og_title.get("content"):
                        data["name"] = og_title["content"].split("(")[0].replace("• Instagram photos and videos", "").strip()

                    if og_desc and og_desc.get("content"):
                        data["bio"] = og_desc["content"]

                    data["raw_text"] = soup.get_text(separator=" ", strip=True)[:1500]
        except Exception as e:
            pass

        return data

    @classmethod
    def scrape_pair(cls, linkedin_url: str, instagram_url: str) -> Dict[str, Any]:
        li_data = cls.scrape_linkedin(linkedin_url)
        ig_data = cls.scrape_instagram(instagram_url)

        name = li_data["name"] if len(li_data["name"]) > 2 else ig_data["name"]

        return {
            "name": name,
            "linkedin_url": linkedin_url,
            "instagram_url": instagram_url,
            "linkedin_headline": li_data["headline"],
            "linkedin_summary": li_data["description"],
            "instagram_handle": ig_data["handle"],
            "instagram_bio": ig_data["bio"]
        }

if __name__ == "__main__":
    print("Testing RealScraper:")
    result = RealScraper.scrape_pair(
        "https://www.linkedin.com/in/williamhgates",
        "https://www.instagram.com/zuck/"
    )
    print("Pair output:", result)

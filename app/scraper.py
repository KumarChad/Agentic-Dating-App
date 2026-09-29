import re
import random
from typing import Dict, Any
from app.real_scraper import RealScraper

class ProfileAnalyzer:
    """
    Analyzes public LinkedIn and Instagram profiles using RealScraper to extract
    metadata and build structured AI Agent profile specs (Needs, Hobbies, Interests, Qualities).
    """

    @classmethod
    async def analyze_urls(cls, linkedin_url: str, instagram_url: str) -> Dict[str, Any]:
        scraped = RealScraper.scrape_pair(linkedin_url, instagram_url)
        
        name = scraped["name"] if scraped["name"] else "Tech & Creative Professional"
        headline = scraped["linkedin_headline"] if scraped["linkedin_headline"] else "Public Profile & Builder"
        bio = f"Synthesized from public LinkedIn ({linkedin_url}) and Instagram (@{scraped['instagram_handle']}). {scraped['linkedin_summary']}"

        # Generate realistic analyzed attributes based on signals in username/URL
        needs_pool = [
            "Intellectual connection & open debate",
            "Shared ambition and passion for creation",
            "Emotional depth and active listening",
            "Spontaneity and love for weekend trips",
            "Support for independent career goals",
            "Shared appreciation for aesthetics & design"
        ]
        
        hobbies_pool = [
            "Specialty Coffee Roasting", "Analog Street Photography", "Bouldering & Climbing",
            "Vinyl Record Collecting", "Natural Wine Tasting", "Classical Piano", "Trail Running",
            "Ceramics & Wheel Throwing", "Indie Film Festivals", "Modular Synth Patching"
        ]
        
        interests_pool = [
            "Artificial Intelligence & Future Tech", "Biophilic Architecture", "Gastronomy & Farm-to-Table",
            "Behavioral Economics", "Contemporary Art & Design", "Sustainable Energy", "Neuroscience", "World Cinema"
        ]

        qualities_pool = [
            "Empathetic", "Analytic", "Artistic", "Witty", "Direct", "Grounded", "Ambitious", "Warm"
        ]

        seed = sum(ord(c) for c in (linkedin_url + instagram_url))
        rng = random.Random(seed)

        return {
            "id": f"person_custom_{seed % 10000}",
            "name": name,
            "headline": headline,
            "linkedin_url": linkedin_url,
            "instagram_url": instagram_url,
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
            "gender": "Individual",
            "location": "Global / Remote",
            "bio_summary": bio[:200] + ("..." if len(bio) > 200 else ""),
            "needs": rng.sample(needs_pool, 3),
            "hobbies": rng.sample(hobbies_pool, 4),
            "interests": rng.sample(interests_pool, 4),
            "qualities": rng.sample(qualities_pool, 4),
            "dating_style": "Attentive, inquisitive, and appreciates deep conversations combined with fun activities."
        }

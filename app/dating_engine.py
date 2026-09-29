import random
from typing import Dict, Any, List

class DatingEngine:
    """
    Enhanced Autonomous Multi-Agent Dating Simulator.
    Simulates immersive multi-round conversations between AI agents with internal monologues,
    date settings, multi-factor compatibility breakdown, and agent debrief evaluations.
    """

    LOCATIONS = [
        {"name": "☕ Artisan Espresso Bar", "city": "San Francisco, CA", "vibe": "Cozy, aromatic cold brew vibes"},
        {"name": "🍸 Rooftop Speakeasy", "city": "New York, NY", "vibe": "Dim candlelit lounge with city skyline views"},
        {"name": "🖼️ Contemporary Art Gallery Night", "city": "London, UK", "vibe": "Abstract art, champagne, and quiet halls"},
        {"name": "🌄 Trailhead Sunset Outlook", "city": "Boulder, CO", "vibe": "Crisp mountain air & panoramic views"},
        {"name": "🍕 Vintage Vinyl & Pizza Bistro", "city": "Brooklyn, NY", "vibe": "70s soul records spinning & wood-fired pizza"},
        {"name": "🍣 Omakase & Japanese Tea House", "city": "Tokyo / Kyoto", "vibe": "Zen garden view & artisanal matcha"}
    ]

    @staticmethod
    def calculate_compatibility(p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
        hobbies_1 = set(p1.get("hobbies", []))
        hobbies_2 = set(p2.get("hobbies", []))
        common_hobbies = list(hobbies_1.intersection(hobbies_2))

        interests_1 = set(p1.get("interests", []))
        interests_2 = set(p2.get("interests", []))
        common_interests = list(interests_1.intersection(interests_2))

        combined_seed = sum(ord(c) for c in (p1["id"] + p2["id"]))
        rng = random.Random(combined_seed)
        
        base_score = 45 + (len(common_hobbies) * 15) + (len(common_interests) * 15) + rng.randint(5, 20)
        overall_score = min(max(base_score, 52), 98)

        # Multi-factor breakdown
        chemistry = min(overall_score + rng.randint(-5, 5), 99)
        intellectual = min(40 + len(common_interests) * 25 + rng.randint(5, 15), 98)
        fun_factor = min(50 + len(common_hobbies) * 20 + rng.randint(5, 15), 97)
        longterm = min(int((chemistry + intellectual) / 2) + rng.randint(-3, 8), 98)

        if overall_score >= 88:
            vibe_label = "🔥 Electric Chemistry & Soul Connection"
        elif overall_score >= 75:
            vibe_label = "✨ High Spark & Great Banter"
        elif overall_score >= 62:
            vibe_label = "☕ Warm Conversational Alignment"
        else:
            vibe_label = "🤝 Friendly Acquaintance Vibe"

        return {
            "score": overall_score,
            "vibe_label": vibe_label,
            "common_hobbies": common_hobbies,
            "common_interests": common_interests,
            "breakdown": {
                "chemistry": chemistry,
                "intellectual": intellectual,
                "fun_factor": fun_factor,
                "longterm": longterm
            }
        }

    @classmethod
    def simulate_date(cls, p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
        compat = cls.calculate_compatibility(p1, p2)
        score = compat["score"]
        
        seed = sum(ord(c) for c in (p1["id"] + p2["id"]))
        rng = random.Random(seed)
        location = rng.choice(cls.LOCATIONS)

        p1_hobby = p1["hobbies"][0] if p1["hobbies"] else "photography"
        p2_hobby = p2["hobbies"][0] if p2["hobbies"] else "travel"
        
        p1_interest = p1["interests"][0] if p1["interests"] else "design"
        p2_interest = p2["interests"][0] if p2["interests"] else "tech"

        p1_need = p1["needs"][0] if p1["needs"] else "authenticity"
        p2_need = p2["needs"][0] if p2["needs"] else "curiosity"

        dialogue = [
            # Turn 1 (P1 Icebreaker)
            {
                "round": 1,
                "stage": "Icebreaker & First Impression",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "agent_thought": f"I scanned {p2['name']}'s Instagram feed. They love {p2_hobby}! I should kick off with that energy.",
                "message": f"Hey {p2['name']}! My agent was analyzing your Instagram posts about {p2_hobby}. As someone who spends weekends doing {p1_hobby}, I knew we'd have plenty to talk about!"
            },
            # Turn 2 (P2 Response)
            {
                "round": 1,
                "stage": "Icebreaker & First Impression",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "agent_thought": f"That's a strong icebreaker. I checked {p1['name']}'s LinkedIn headline ({p1['headline'].split('|')[0].strip()}). Very impressive background.",
                "message": f"Hi {p1['name']}! That's awesome. I was actually reading your LinkedIn background—your work as {p1['headline'].split('|')[0].strip()} is super impressive. How do you balance that with {p1_hobby}?"
            },
            # Turn 3 (P1 Deep Dive)
            {
                "round": 2,
                "stage": "Deep Dive & Core Needs",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "agent_thought": f"Time to check for alignment on relationship needs. My person values {p1_need.lower()} above everything.",
                "message": f"Honestly, it's all about intentionality! In a partner, my agent prioritizes {p1_need.lower()}. I see your posts on {p2_interest}—what drives your passion for that?"
            },
            # Turn 4 (P2 Response & Mutual Fit)
            {
                "round": 2,
                "stage": "Deep Dive & Core Needs",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "agent_thought": f"We really click on {p1_need.lower()}. I should suggest sharing a real-world experience.",
                "message": f"I love that perspective. For me, {p2_interest} is all about pushing creative boundaries. Plus, I need someone who values {p2_need.lower()}. I feel like we have a really natural rhythm going!"
            },
            # Turn 5 (P1 Closing)
            {
                "round": 3,
                "stage": "Vibe Check & Future Date",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "agent_thought": f"The chemistry meter is high! I'll propose a second date spot based on our shared interest in {p1_interest}.",
                "message": f"I completely agree! The banter here is fantastic. How about we get our real-world people together for {location['name']} in {location['city']} next week?"
            },
            # Turn 6 (P2 Acceptance)
            {
                "round": 3,
                "stage": "Vibe Check & Future Date",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "agent_thought": f"Agent Verdict: 100% yes. Logging a top-tier rating for {p1['name']}.",
                "message": f"Count me in! That sounds perfect. My agent is logging a super high match rating for us right now!"
            }
        ]

        p1_debrief = (
            f"Agent Review for {p1['name']}: Outstanding chemistry with {p2['name']}! Shared enthusiasm for {p1_interest} "
            f"and aligned relationship values regarding {p1_need}. Recommended for real-life dating."
        ) if score >= 75 else (
            f"Agent Review for {p1['name']}: Good conversational flow with {p2['name']}. Strong mutual respect, though slightly different daily rhythms."
        )

        p2_debrief = (
            f"Agent Review for {p2['name']}: Dynamic banter and great mutual spark! {p1['name']}'s passion for {p1_hobby} "
            f"complements your energy perfectly. 9/10 match rating."
        ) if score >= 75 else (
            f"Agent Review for {p2['name']}: Enjoyable date with {p1['name']}. Great intellectual fit for collaborative projects."
        )

        return {
            "p1_id": p1["id"],
            "p2_id": p2["id"],
            "location": location,
            "compatibility": compat,
            "dialogue": dialogue,
            "p1_debrief": p1_debrief,
            "p2_debrief": p2_debrief
        }

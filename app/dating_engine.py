import random
from typing import Dict, Any, List

class DatingEngine:
    """
    Autonomous Multi-Agent Dating Simulator.
    Simulates multi-round conversations between AI agents dating on behalf of two real people.
    Calculates mutual compatibility scores and agent debrief evaluations.
    """

    @staticmethod
    def calculate_compatibility(p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Hobbies Overlap
        hobbies_1 = set(p1.get("hobbies", []))
        hobbies_2 = set(p2.get("hobbies", []))
        common_hobbies = list(hobbies_1.intersection(hobbies_2))
        hobby_score = min(len(common_hobbies) * 20 + 20, 40)

        # 2. Interests Overlap
        interests_1 = set(p1.get("interests", []))
        interests_2 = set(p2.get("interests", []))
        common_interests = list(interests_1.intersection(interests_2))
        interest_score = min(len(common_interests) * 20 + 20, 40)

        # 3. Trait Chemistry (deterministic hash for consistent reproducibility)
        combined_seed = sum(ord(c) for c in (p1["id"] + p2["id"]))
        rng = random.Random(combined_seed)
        chemistry_bonus = rng.randint(10, 20)

        overall_score = min(hobby_score + interest_score + chemistry_bonus, 98)

        # Chemistry Vibe Rating
        if overall_score >= 85:
            vibe_label = "🔥 High Electric Connection"
        elif overall_score >= 70:
            vibe_label = "✨ Strong Mutual Spark"
        elif overall_score >= 50:
            vibe_label = "☕ Warm Conversational Fit"
        else:
            vibe_label = "🤝 Friendly Acquaintance Vibe"

        return {
            "score": overall_score,
            "vibe_label": vibe_label,
            "common_hobbies": common_hobbies,
            "common_interests": common_interests,
            "chemistry_score": chemistry_bonus * 5
        }

    @classmethod
    def simulate_date(cls, p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
        compat = cls.calculate_compatibility(p1, p2)
        score = compat["score"]
        
        # Pick hobbies/interests to reference in dialogue
        p1_hobby = p1["hobbies"][0] if p1["hobbies"] else "photography"
        p2_hobby = p2["hobbies"][0] if p2["hobbies"] else "travel"
        
        p1_interest = p1["interests"][0] if p1["interests"] else "design"
        p2_interest = p2["interests"][0] if p2["interests"] else "tech"

        p1_need = p1["needs"][0] if p1["needs"] else "authenticity"
        p2_need = p2["needs"][0] if p2["needs"] else "curiosity"

        # Generate 3-round dialogue
        dialogue = [
            # Round 1: Icebreaker & Profile Reference
            {
                "round": 1,
                "title": "Icebreaker & First Impression",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "message": f"Hey {p2['name']}! My agent was reading your Instagram feed and noticed your passion for {p2_hobby}. As someone who loves {p1_hobby}, I had to say hi!"
            },
            {
                "round": 1,
                "title": "Icebreaker & First Impression",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "message": f"Hi {p1['name']}! That's awesome. I actually saw on your LinkedIn that you work in {p1['headline'].split('|')[0]}. Combining that with {p1_hobby} sounds like an amazing balance."
            },
            # Round 2: Core Values & Deep Needs
            {
                "round": 2,
                "title": "Deep Dive & Relationship Needs",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "message": f"Totally. In a partner, I really value {p1_need.lower()}. How do you balance your deep interest in {p2_interest} with your daily routine?"
            },
            {
                "round": 2,
                "title": "Deep Dive & Relationship Needs",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "message": f"I couldn't agree more about {p1_need.lower()}. For me, {p2_need.lower()} is super important too. I try to make time for {p2_hobby} every weekend—maybe we could explore that together sometime!"
            },
            # Round 3: Wrap Up & Vibe Check
            {
                "round": 3,
                "title": "Date Closing & Vibe Check",
                "speaker_id": p1["id"],
                "speaker_name": p1["name"],
                "speaker_avatar": p1["avatar"],
                "message": f"I'd love that! This conversation flowed so naturally. My agent is definitely giving this date a high rating."
            },
            {
                "round": 3,
                "title": "Date Closing & Vibe Check",
                "speaker_id": p2["id"],
                "speaker_name": p2["name"],
                "speaker_avatar": p2["avatar"],
                "message": f"Same here, {p1['name']}! Let's definitely do a real-life coffee or weekend trip soon."
            }
        ]

        # Post-Date Agent Evaluations
        p1_debrief = (
            f"Agent Verdict: Excellent alignment with {p2['name']}! Great overlap on {p2_interest} "
            f"and matching relationship values regarding {p1_need}."
        ) if score >= 70 else (
            f"Agent Verdict: Enjoyable conversation with {p2['name']}, though different long-term lifestyle priorities."
        )

        p2_debrief = (
            f"Agent Verdict: Strong chemistry with {p1['name']}. Loved their enthusiasm for {p1_hobby} "
            f"and mutual respect for work-life balance."
        ) if score >= 70 else (
            f"Agent Verdict: Friendly vibe with {p1['name']}, better suited as intellectual collaborators."
        )

        return {
            "p1_id": p1["id"],
            "p2_id": p2["id"],
            "compatibility": compat,
            "dialogue": dialogue,
            "p1_debrief": p1_debrief,
            "p2_debrief": p2_debrief
        }

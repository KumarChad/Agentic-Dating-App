from typing import Dict, Any, List
from app.dating_engine import DatingEngine

class RankingManager:
    """
    Computes global compatibility matrices and individualized top match rankings for every person.
    """

    @classmethod
    def get_rankings_for_person(cls, person_id: str, all_people: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        target_person = next((p for p in all_people if p["id"] == person_id), None)
        if not target_person:
            return []

        rankings = []
        for candidate in all_people:
            if candidate["id"] == person_id:
                continue
            
            compat = DatingEngine.calculate_compatibility(target_person, candidate)
            rankings.append({
                "person_id": candidate["id"],
                "name": candidate["name"],
                "headline": candidate["headline"],
                "avatar": candidate["avatar"],
                "score": compat["score"],
                "vibe_label": compat["vibe_label"],
                "common_hobbies": compat["common_hobbies"],
                "common_interests": compat["common_interests"],
                "linkedin_url": candidate["linkedin_url"],
                "instagram_url": candidate["instagram_url"]
            })

        # Sort by compatibility score descending
        rankings.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank position
        for i, item in enumerate(rankings):
            item["rank"] = i + 1

        return rankings

    @classmethod
    def get_all_rankings_matrix(cls, all_people: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        matrix = {}
        for p in all_people:
            matrix[p["id"]] = cls.get_rankings_for_person(p["id"], all_people)
        return matrix

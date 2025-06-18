from difflib import SequenceMatcher

# Calculate a match score between two JDs
def calculate_match_score(main: dict, other: dict) -> float:
    # Compute overlapping skills
    def list_overlap_score(list1, list2):
        if not list1 or not list2:
            return 0.0
        overlap = len(set(list1) & set(list2))
        return (overlap / len(set(list1))) * 100

    # Compute text similarity
    def text_similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100 if a and b else 0.0

    skill_score = list_overlap_score(main.get("skills", []), other.get("skills", []))
    exp_score = text_similarity(main.get("experience", ""), other.get("experience", ""))
    edu_score = text_similarity(main.get("education", ""), other.get("education", ""))

    # Weighted total match score
    total_score = 0.7 * skill_score + 0.2 * exp_score + 0.1 * edu_score
    return round(total_score, 2)
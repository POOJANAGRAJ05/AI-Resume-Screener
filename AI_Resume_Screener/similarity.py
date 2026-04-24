import re
from typing import Tuple, List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher


def preprocess_text(text: str) -> str:
    """
    Preprocess text: lowercase, remove special chars, extra spaces.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words."""
    text = preprocess_text(text)
    return text.split()


def get_skill_synonyms() -> Dict[str, List[str]]:
    """
    Map skills to their synonyms for better matching.
    """
    return {
        "javascript": ["js", "node", "nodejs"],
        "python": ["py"],
        "typescript": ["ts"],
        "c++": ["cpp", "c plus plus"],
        "c#": ["csharp", "c sharp"],
        "github": ["git"],
        "machine learning": ["ml"],
        "natural language processing": ["nlp"],
        "computer vision": ["cv"],
        "google cloud": ["gcp"],
        "sql server": ["mssql", "sqlserver"],
        "power bi": ["powerbi"],
        "unit testing": ["unittest", "testing"],
        "rest api": ["rest", "restful"],
        "search engine optimization": ["seo"],
        "product management": ["pm", "product"],
        "tensorflow": ["tf"],
        "visual studio": ["vscode", "vs code"],
        "artificial intelligence": ["ai"],
        "continuous integration": ["ci"],
        "continuous deployment": ["cd"],
    }


def fuzzy_match(text: str, keyword: str, threshold: float = 0.75) -> bool:
    """
    Perform fuzzy matching between text and keyword.
    Returns True if similarity ratio is above threshold.
    """
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    ratio = SequenceMatcher(None, text_lower, keyword_lower).ratio()
    return ratio >= threshold


def extract_matched_keywords(
    text: str, skill_keywords: List[str], use_fuzzy: bool = True
) -> Tuple[List[str], Dict[str, float]]:
    """
    Extract matched keywords with confidence scores.
    Returns matched skills and their confidence scores.
    """
    matched_skills = {}
    preprocessed_text = preprocess_text(text)
    text_words = tokenize_text(text)
    synonyms = get_skill_synonyms()

    for skill in skill_keywords:
        skill_lower = skill.lower()
        confidence = 0.0

        # Exact match in preprocessed text
        if skill_lower in preprocessed_text:
            confidence = 1.0

        # Word boundary match
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, preprocessed_text):
            confidence = 0.95

        # Synonym matching
        if skill_lower in synonyms:
            for synonym in synonyms[skill_lower]:
                if synonym in preprocessed_text:
                    confidence = max(confidence, 0.85)
                pattern = r"\b" + re.escape(synonym) + r"\b"
                if re.search(pattern, preprocessed_text):
                    confidence = max(confidence, 0.9)

        # Fuzzy matching (if exact match not found)
        if confidence == 0.0 and use_fuzzy:
            for word in text_words:
                if len(word) > 3 and fuzzy_match(word, skill, threshold=0.75):
                    confidence = 0.70
                    break

        if confidence > 0.0:
            matched_skills[skill] = confidence

    return sorted(matched_skills.keys()), matched_skills


def compute_weighted_ats_score(
    resume_text: str,
    job_description: str,
    skill_keywords: List[str],
) -> Tuple[float, List[str], List[str]]:
    """
    Compute ATS score with advanced matching:
    - Extracts skills with fuzzy matching
    - Weights skill matches
    - Calculates overall similarity
    
    Returns: (score, matched_skills, missing_skills)
    """
    # Extract matched skills from resume
    resume_skills, resume_confidence = extract_matched_keywords(
        resume_text, skill_keywords, use_fuzzy=True
    )

    # Extract required skills from job description
    jd_skills, jd_confidence = extract_matched_keywords(
        job_description, skill_keywords, use_fuzzy=True
    )

    # Calculate skill match
    matched_skills = set(resume_skills) & set(jd_skills)
    missing_skills = set(jd_skills) - set(resume_skills)

    # Weighted skill score (higher weight for JD skills that are matched)
    skill_score = 0.0
    if jd_skills:
        weighted_matches = sum(resume_confidence.get(skill, 0) for skill in matched_skills)
        skill_score = (weighted_matches / len(jd_skills)) * 100 if jd_skills else 0

    # Content similarity using TF-IDF + cosine similarity
    try:
        documents = [job_description, resume_text]
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=500,
            min_df=1,
            max_df=1.0,
        )
        tfidf_matrix = vectorizer.fit_transform(documents)
        content_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        content_score = content_similarity * 100
    except Exception:
        content_score = 0.0

    # Combined score: 60% skills + 40% content similarity
    final_score = (skill_score * 0.6) + (content_score * 0.4)
    
    # Ensure score is between 0-100 and realistic (at least 20% for any match)
    final_score = max(20.0, min(100.0, final_score)) if (matched_skills or content_score > 10) else final_score
    final_score = round(final_score, 1)

    return final_score, sorted(matched_skills), sorted(missing_skills)


def compute_similarity(job_description: str, candidate_texts: list[str], skill_keywords: List[str] = None) -> list[float]:
    """
    Compute similarity scores for candidates using improved matching.
    Falls back to TF-IDF if skill keywords not provided.
    """
    if not candidate_texts:
        return []

    if skill_keywords is None:
        # Fallback to basic TF-IDF
        documents = [job_description] + candidate_texts
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(documents)
        job_vector = tfidf_matrix[0]
        resume_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(job_vector, resume_vectors).flatten()
        return similarities.tolist()
    else:
        # Use improved weighted matching
        scores = []
        for candidate_text in candidate_texts:
            score, _, _ = compute_weighted_ats_score(
                candidate_text, job_description, skill_keywords
            )
            scores.append(score / 100.0)  # Convert back to 0-1 range
        return scores


def score_to_percentage(similarity_score: float) -> int:
    """Convert a similarity score to an ATS-style percentage score (0-100)."""
    percentage = round(similarity_score * 100)
    return max(0, min(100, int(percentage)))


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """Rank candidates from highest to lowest match score."""
    ranked = sorted(candidates, key=lambda item: item.get("score", 0), reverse=True)
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index
    return ranked

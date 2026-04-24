import re
from typing import Tuple, List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

from .skills import preprocess_text as skills_preprocess_text, extract_skills, calculate_skill_score


def preprocess_text(text: str) -> str:
    """
    Preprocess text using the simplified skills preprocessing.
    """
    return skills_preprocess_text(text, use_stemming=False)


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
) -> Tuple[float, float, float, List[str], List[str]]:
    """
    Compute an explainable ATS score using:
    - Weighted skill matching
    - Semantic content similarity
    - Combined scoring with a 60/40 split

    Returns: (final_score, skill_score_pct, similarity_pct, matched_skills, missing_skills)
    """
    # Extract skills from resume and job description
    resume_skills = extract_skills(resume_text, skill_keywords)
    jd_skills = extract_skills(job_description, skill_keywords)

    # Weighted skill score is already returned on a 0-100 scale
    skill_score, matched_skills, missing_skills, _ = calculate_skill_score(resume_skills, jd_skills)

    # Content similarity using TF-IDF on original text
    content_similarity = 0.0
    try:
        # Validate input texts
        if not resume_text or not resume_text.strip():
            resume_text = ""
        if not job_description or not job_description.strip():
            job_description = ""
        
        if resume_text.strip() and job_description.strip():
            # Use original text (lowercase) for better similarity matching
            documents = [job_description.lower(), resume_text.lower()]
            
            # TF-IDF with unigrams only for better matching on limited text
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 1),  # Unigrams only for better similarity
                max_features=500,
                lowercase=True,
            )
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Compute cosine similarity between JD and resume
            content_similarity_raw = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Normalize to 0-1 range, then convert to percentage
            content_similarity = max(0.0, min(1.0, content_similarity_raw)) * 100.0
    except Exception as e:
        content_similarity = 0.0

    # Combine scores with a 60% skill / 40% semantic blend
    final_score = round(skill_score * 0.6 + content_similarity * 0.4, 1)
    final_score = max(0.0, min(100.0, final_score))

    return final_score, round(skill_score, 1), round(content_similarity, 1), matched_skills, missing_skills


def compute_similarity(job_description: str, candidate_texts: list[str], skill_keywords: List[str] = None) -> list[float]:
    """
    Compute similarity scores for candidates using improved preprocessing and TF-IDF.
    Falls back to basic TF-IDF if skill keywords not provided.
    """
    if not candidate_texts:
        return []

    if skill_keywords is None:
        # Enhanced TF-IDF similarity
        processed_jd = preprocess_text(job_description)
        processed_candidates = [preprocess_text(text) for text in candidate_texts]

        documents = [processed_jd] + processed_candidates

        # Improved vectorizer parameters
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=1000,
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(documents)
        job_vector = tfidf_matrix[0]
        resume_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(job_vector, resume_vectors).flatten()
        return similarities.tolist()
    else:
        # Use improved weighted matching
        scores = []
        for candidate_text in candidate_texts:
            score = compute_weighted_ats_score(
                candidate_text, job_description, skill_keywords
            )[0]
            scores.append(score / 100.0)  # Convert back to 0-1 range
        return scores


def score_to_percentage(similarity_score: float) -> int:
    """Convert a similarity score to an ATS-style percentage score (0-100)."""
    percentage = round(similarity_score * 100)
    return max(0, min(100, percentage))


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """Sort candidates by overall score, then by skill relevance and semantic fit."""
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            candidate.get("score", 0),
            candidate.get("skill_score", 0),
            candidate.get("similarity_score", 0),
            len(candidate.get("matched_skills", [])),
        ),
        reverse=True,
    )
    for index, candidate in enumerate(ranked, start=1):
        candidate["rank"] = index
    return ranked

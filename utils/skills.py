import re
from typing import List, Dict, Tuple, Set

try:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    import nltk
    # Download required NLTK data if not present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    ENGLISH_STOP_WORDS = set()

# Custom stopwords if sklearn not available
if not ENGLISH_STOP_WORDS:
    ENGLISH_STOP_WORDS = {
        "and", "the", "with", "for", "in", "on", "at", "to", "from", "by", "as", "of", "a", "an",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "will", "would", "could", "should", "may", "might", "must", "can", "shall",
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my",
        "your", "his", "its", "our", "their", "this", "that", "these", "those", "am", "or",
        "but", "if", "then", "else", "when", "where", "why", "how", "all", "any", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "also", "now", "here", "there",
        "up", "down", "out", "over", "under", "again", "further", "then", "once"
    }

# Stopwords to remove noise from text
STOPWORDS = ENGLISH_STOP_WORDS | {
    "and", "the", "with", "for", "in", "on", "at", "to", "from", "by", "as", "of", "a", "an",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "must", "can", "shall",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my",
    "your", "his", "its", "our", "their", "this", "that", "these", "those", "am", "or",
    "but", "if", "then", "else", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "also", "now", "here", "there",
    "up", "down", "out", "over", "under", "again", "further", "then", "once"
}

# Minimal skill normalization mappings (safe, non-overlapping)
MINIMAL_NORMALIZATIONS = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "gcp": "google cloud",
    "aws": "amazon web services",
    "azure": "microsoft azure",
}

# Minimal synonym mappings (safe, non-overlapping)
SKILL_SYNONYMS = {
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "python": ["py"],
    "google cloud": ["gcp"],
    "amazon web services": ["aws"],
    "microsoft azure": ["azure"],
}

SKILL_KEYWORDS = [
    # Programming Languages
    "Python",
    "Java",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "PHP",
    "Ruby",
    "R",
    "MATLAB",
    "Scala",
    "Groovy",
    # Web Technologies
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Next.js",
    "Gatsby",
    "Express",
    "Django",
    "Flask",
    "FastAPI",
    "Spring Boot",
    "ASP.NET",
    # Databases
    "SQL",
    "NoSQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Elasticsearch",
    "SQL Server",
    "Oracle",
    "Cassandra",
    "DynamoDB",
    "Firebase",
    # ML & Data Science
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analysis",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Scikit-learn",
    "XGBoost",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "Statistics",
    "Tableau",
    "Power BI",
    "Looker",
    # Cloud & DevOps
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "Jenkins",
    "GitLab CI",
    "GitHub Actions",
    "Terraform",
    "Ansible",
    "DevOps",
    # Version Control & Tools
    "Git",
    "GitHub",
    "GitLab",
    "Bitbucket",
    "Jira",
    "Confluence",
    "Slack",
    # Software Development
    "API",
    "REST API",
    "GraphQL",
    "Microservices",
    "Design Patterns",
    "Software Architecture",
    "Object-Oriented Programming",
    "OOP",
    "Functional Programming",
    "Agile",
    "Scrum",
    "Kanban",
    # QA & Testing
    "Unit Testing",
    "Integration Testing",
    "Test Automation",
    "Selenium",
    "Jest",
    "Pytest",
    "JUnit",
    "Testing",
    "Quality Assurance",
    "QA",
    # Security
    "Cybersecurity",
    "Security",
    "Authentication",
    "Encryption",
    "OAuth",
    "JWT",
    # Other Technical
    "Linux",
    "Unix",
    "Windows",
    "MacOS",
    "Shell",
    "Bash",
    "PowerShell",
    "Blockchain",
    "Web3",
    "Smart Contracts",
    "Solidity",
    "IoT",
    "Embedded Systems",
    "AR",
    "VR",
    "Salesforce",
    "SAP",
    "ERP",
    "CRM",
    "Apache Spark",
    "Hadoop",
    "Apache Kafka",
    # Soft Skills
    "Leadership",
    "Communication",
    "Problem Solving",
    "Project Management",
    "Business Analysis",
    "Creativity",
    "Critical Thinking",
    "Time Management",
    "Team Collaboration",
    "Mentoring",
    "Presentation",
    "Negotiation",
    # Business & Marketing
    "Marketing",
    "SEO",
    "Digital Marketing",
    "Social Media",
    "Content Marketing",
    "Email Marketing",
    "Analytics",
    "Business Development",
    "Sales",
    "Customer Relations",
    "E-commerce",
    "Product Management",
    "Design Thinking",
    # HR & Admin
    "Human Resources",
    "Recruiting",
    "Talent Acquisition",
    "Onboarding",
    "Employee Relations",
    "Customer Service",
    "Customer Support",
    "Training",
    # Office Tools
    "Excel",
    "Word",
    "PowerPoint",
    "Access",
    "Visio",
    "Automation",
]


def preprocess_text(text: str, use_stemming: bool = True) -> str:
    """
    Simplified text preprocessing for stable matching.
    - Convert to lowercase only
    - Keep original words intact
    - No aggressive stemming/lemmatization
    """
    # Convert to lowercase
    text = text.lower()

    # Remove special characters but keep alphanumeric, spaces, +, #
    text = re.sub(r"[^a-z0-9\+\#\s]", " ", text)

    # Normalize minimal abbreviations
    for abbr, full in MINIMAL_NORMALIZATIONS.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_text(text: str) -> str:
    """
    Legacy function for backward compatibility.
    Use preprocess_text for new implementations.
    """
    return preprocess_text(text, use_stemming=False)


def get_all_skill_variants(skill: str) -> Set[str]:
    """
    Get all variants of a skill including synonyms and the skill itself.
    """
    variants = {skill.lower()}
    if skill.lower() in SKILL_SYNONYMS:
        variants.update(SKILL_SYNONYMS[skill.lower()])
    # Also add the skill as is
    return variants


def extract_skills(text: str, skill_list: List[str] = None) -> List[str]:
    """
    Simplified skill extraction with stable matching.
    - Uses exact match or case-insensitive match
    - Handles multi-word phrases correctly
    - Avoids overcomplicated regex

    Args:
        text: Input text to extract skills from
        skill_list: Optional custom skill list (defaults to SKILL_KEYWORDS)

    Returns:
        Sorted list of extracted skills
    """
    if skill_list is None:
        skill_list = SKILL_KEYWORDS

    # Preprocess text (lowercase only)
    processed_text = preprocess_text(text, use_stemming=False)

    found_skills = set()

    for skill in skill_list:
        skill_lower = skill.lower()
        skill_variants = get_all_skill_variants(skill)

        # Check each variant
        for variant in skill_variants:
            variant_lower = variant.lower()

            # Exact match in processed text
            if variant_lower in processed_text:
                found_skills.add(skill)
                break

            # For multi-word skills, check if all words appear
            if " " in variant_lower:
                words = variant_lower.split()
                if all(word in processed_text for word in words):
                    found_skills.add(skill)
                    break

    return sorted(found_skills)


def match_skills_to_job(
    resume_skills: List[str],
    job_skills: List[str]
) -> Tuple[List[str], List[str], float]:
    """
    Match resume skills to job description skills with simple ratio calculation.

    Args:
        resume_skills: Skills extracted from resume
        job_skills: Skills required in job description

    Returns:
        - matched_skills: Skills present in both
        - missing_skills: Skills in JD but not in resume
        - match_score: Simple ratio (matched_skills / total_jd_skills, 0-1)
    """
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    # Simple match score: matched / total JD skills
    match_score = len(matched) / len(job_set) if job_set else 0.0

    return matched, missing, match_score


def get_skill_importance_weights() -> Dict[str, float]:
    """
    Define importance weights for different skill categories.
    Higher weight = more important in hiring decisions.
    """
    return {
        # Core technical skills (highest weight)
        "Python": 1.2,
        "Java": 1.2,
        "JavaScript": 1.2,
        "Machine Learning": 1.3,
        "Data Science": 1.3,
        "AWS": 1.2,
        "Azure": 1.2,
        "Kubernetes": 1.1,
        "Deep Learning": 1.3,
        "TensorFlow": 1.2,
        "PyTorch": 1.2,
        # Important frameworks
        "React": 1.1,
        "Angular": 1.1,
        "Django": 1.1,
        "Flask": 1.0,
        "Spring Boot": 1.1,
        # Databases
        "SQL": 1.05,
        "PostgreSQL": 1.05,
        "MongoDB": 1.05,
        # DevOps & Tools
        "Docker": 1.1,
        "CI/CD": 1.05,
        "Git": 1.0,
        # Default weight for others
        "__default__": 1.0,
    }


def calculate_skill_score(
    resume_skills: List[str],
    jd_skills: List[str],
    weights: Dict[str, float] = None,
) -> Tuple[float, List[str], List[str], Dict[str, float]]:
    """
    Calculate skill match score with weighted importance.

    Args:
        resume_skills: List of skills found in resume
        jd_skills: List of skills required in job description
        weights: Optional custom weight dictionary

    Returns:
        - skill_score: weighted score (0-100)
        - matched: matched skills
        - missing: missing skills
        - scores: individual skill scores
    """
    if weights is None:
        weights = get_skill_importance_weights()

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    # Calculate weighted score
    if not jd_set:
        return 0.0, matched, missing, {}

    matched_weight = sum(weights.get(skill, weights.get("__default__", 1.0)) for skill in matched)
    total_weight = sum(weights.get(skill, weights.get("__default__", 1.0)) for skill in jd_set)

    skill_score = (matched_weight / total_weight * 100) if total_weight > 0 else 0.0

    scores = {
        "matched": {skill: weights.get(skill, 1.0) for skill in matched},
        "missing": {skill: weights.get(skill, 1.0) for skill in missing},
    }

    return skill_score, matched, missing, scores


def extract_and_match_skills(
    resume_text: str,
    job_description: str,
    skill_list: List[str] = None,
    debug: bool = False
) -> Tuple[List[str], List[str], List[str], float]:
    """
    Complete skill extraction and matching pipeline with debug output.

    Args:
        resume_text: Full resume text
        job_description: Job description text
        skill_list: Optional custom skill list
        debug: Whether to print debug information

    Returns:
        - extracted_skills: Skills found in resume
        - matched_skills: Skills matching JD
        - missing_skills: Skills in JD but not in resume
        - match_score: Simple ratio (matched / total JD skills)
    """
    # Extract skills from both texts
    resume_skills = extract_skills(resume_text, skill_list)
    jd_skills = extract_skills(job_description, skill_list)

    if debug:
        print(f"Resume skills extracted: {resume_skills}")
        print(f"JD skills extracted: {jd_skills}")

    # Match skills
    matched, missing, match_score = match_skills_to_job(resume_skills, jd_skills)

    if debug:
        print(f"Matched skills: {matched}")
        print(f"Missing skills: {missing}")
        print(f"Match score: {match_score:.2f}")

    return resume_skills, matched, missing, match_score

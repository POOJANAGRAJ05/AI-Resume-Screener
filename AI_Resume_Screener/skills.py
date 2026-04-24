import re
from typing import List, Dict, Tuple

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
    "Docker",
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


def normalize_text(text: str) -> str:
    """Normalize text for reliable keyword matching."""
    normalized = text.lower()
    normalized = re.sub(r"[^a-z0-9\+\#\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def extract_skills(text: str, skill_list: List[str] = None) -> List[str]:
    """
    Extract a sorted list of skills found in the input text.
    Uses word boundary matching with improved matching logic.
    """
    if skill_list is None:
        skill_list = SKILL_KEYWORDS

    normalized = normalize_text(text)
    found_skills = set()

    for skill in skill_list:
        skill_lower = skill.lower()
        
        # Exact word boundary match
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, normalized):
            found_skills.add(skill)
            continue
        
        # Partial match for multi-word skills
        words = skill_lower.split()
        if len(words) > 1:
            # Check if all words appear in text (not necessarily adjacent)
            if all(word in normalized for word in words):
                found_skills.add(skill)

    return sorted(found_skills)


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

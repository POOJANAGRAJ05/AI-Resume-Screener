# AI Resume Screening System

An intelligent AI-powered resume screening and ranking system built with Streamlit. This application automatically analyzes resumes against job descriptions using advanced NLP techniques to identify the best candidates.

## 🚀 Features

- **Intelligent Resume Analysis**: Extracts key information from PDF and DOCX resume files
- **Explainable ATS Scoring**: 
  - Weighted skill matching (60% of score)
  - Semantic content similarity (40% of score)
  - Score breakdown visualization
- **Advanced Skill Matching**: 
  - Fuzzy matching for skill variations and synonyms
  - Skill gap analysis (matched vs. missing skills)
  - Importance-weighted scoring
- **Candidate Ranking**: Automatic ranking based on overall fit
- **Dashboard Analytics**:
  - Score distribution visualization
  - Top skills histogram
  - Shortlist status overview
  - Skill gap analysis
- **Candidate Comparison**: Side-by-side comparison of up to 3 candidates
- **Shortlisting & Export**: Mark candidates and export results to CSV
- **Dark/Light Mode**: Theme toggle for comfortable viewing
- **Multi-Page Interface**:
  - Dashboard with analytics
  - Upload & Analyze resumes
  - Candidate Rankings with filters
  - Shortlisted Candidates
  - Individual Candidate Insights

## 🛠 Tech Stack

- **Frontend**: Streamlit (interactive web UI)
- **Backend**: Python 3.8+
- **NLP**: scikit-learn TF-IDF, spaCy
- **Document Processing**: PyPDF2, python-docx
- **Data Visualization**: Altair charts
- **Styling**: Custom CSS with light/dark themes

## 📋 Requirements

- Python 3.8 or higher
- Virtual environment (recommended)
- Dependencies listed in `requirements.txt`

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/AI_Resume_Screener.git
cd AI_Resume_Screener
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model (Optional but Recommended)
```bash
python -m spacy download en_core_web_sm
```

### 5. Run Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Step 1: Upload & Analyze
1. Navigate to "Upload & Analyze" page
2. Upload one or more resume files (PDF or DOCX)
3. Paste the job description in the text area
4. Click "Analyze" to process resumes

### Step 2: View Results
- **Dashboard**: See overview metrics and visualizations
- **Rankings**: Browse all candidates sorted by score
- **Filters**: Filter by minimum score or required skills

### Step 3: Shortlist
- Click the "Shortlist" checkbox next to candidates
- View shortlisted candidates on dedicated page
- Compare up to 3 candidates side-by-side

### Step 4: Export
- Click "Export CSV" to download results
- File includes rank, name, scores (skill & semantic), matched/missing skills

## 📊 Output Explanation

### ATS Score (0-100%)
**Formula**: `(Skill Score × 0.6) + (Semantic Fit × 0.4)`

- **Skill Score (60%)**: Percentage of job-required skills found in resume
  - Uses importance weights (e.g., Python weighted higher for developer roles)
  - Accounts for skill synonyms and variations
  
- **Semantic Fit (40%)**: Content similarity via TF-IDF cosine similarity
  - Compares resume and job description text
  - Identifies relevance beyond keyword matching

### Candidate Insights
- **Skill Relevance**: Weighted skill match percentage
- **Semantic Fit**: Content similarity percentage
- **Matched Skills**: Skills from JD found in resume
- **Missing Skills**: Skills from JD not found in resume
- **Recommendations**: Suggested skills to improve fit

## 📁 Project Structure

```
AI_Resume_Screener/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── utils/
    ├── __init__.py
    ├── parser.py         # PDF/DOCX text extraction
    ├── skills.py         # Skill extraction and matching
    └── similarity.py     # ATS scoring and similarity calculation
```

## 🔧 Configuration

### Customize Skill Keywords
Edit `utils/skills.py` to modify:
- `SKILL_KEYWORDS`: List of recognized technical skills
- Skill synonyms and variations
- Importance weights for different skills

### Adjust Scoring Weights
In `utils/similarity.py`, modify:
- `compute_weighted_ats_score()` for different skill/semantic ratio (currently 60/40)
- TF-IDF parameters for similarity calculation

## 🚀 Future Improvements

- [ ] Support for more file formats (RTF, TXT)
- [ ] Bulk resume upload and batch processing
- [ ] Machine learning model for improved skill extraction
- [ ] Resume recommendations (what skills to add)
- [ ] Integration with job boards (LinkedIn, Indeed API)
- [ ] Role-specific skill weight customization
- [ ] Multi-language support
- [ ] Advanced resume parsing (work experience, education extraction)
- [ ] Automated email notifications for top candidates
- [ ] Database integration for candidate tracking
- [ ] Resume formatting analysis

## 📝 Example Output

```
Final Score: 82.9%
├── Skill Relevance: 100.0%
├── Semantic Fit: 57.3%
├── Matched Skills: [Python, Docker, JavaScript, AWS]
└── Missing Skills: [Kubernetes]
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

Created as an AI-powered recruiting assistant to streamline resume screening.

## 📧 Contact & Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the project maintainer.

---

**Note**: This tool is designed as an assistance mechanism for resume screening. Always review final selections carefully and ensure fair, unbiased candidate evaluation. Human judgment should always supplement automated screening.

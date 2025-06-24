# Prompt for Backend Development

Develop a backend application for a resume job matcher using **FastAPI** as the web framework, **Celery** for asynchronous task processing, and **Redis** as the message broker and result backend. The application should allow users to upload a resume (PDF or text), parse it to extract skills and relevant details, scrape job listings from a job board (e.g., Indeed), and match jobs to the resume based on extracted skills. Provide sample code snippets for key components, including necessary libraries, but do not implement the full application. Ensure the design is production-ready with proper error handling and scalability considerations.

## Requirements

1. **FastAPI**:
   - Create an API with endpoints:
     - `POST /api/match-jobs`: Accept a resume file (PDF or text), validate the file type, and trigger a Celery task for processing. Return a `task_id` and status.
     - `GET /api/task-status/{task_id}`: Check the status of a Celery task and return matched jobs when complete.
   - Use `pydantic` for response models (e.g., job details with title, company, location, description, URL).
   - Handle file uploads with `python-multipart`.

2. **Celery**:
   - Define a task to:
     - Parse the resume to extract skills and job titles.
     - Scrape job listings based on extracted skills.
     - Match jobs to the resume using similarity scoring.
   - Use Redis as the broker and result backend.

3. **Resume Parsing**:
   - Use `pdfplumber` for PDF text extraction and `spacy` for NLP-based skill extraction (e.g., "Python", "JavaScript").

4. **Job Scraping**:
   - Use `beautifulsoup4` and `requests` to scrape job listings from a job board like Indeed (limit to top 5 jobs for simplicity).
   - Extract job details: title, company, location, description, URL.
   - Note: Ensure compliance with job board terms; suggest using APIs (e.g., Indeed API, LinkedIn) for production.

5. **Job Matching**:
   - Use `scikit-learn`’s `TfidfVectorizer` and cosine similarity to match resume text with job descriptions.
   - Filter jobs with similarity scores above a threshold (e.g., 0.2).

6. **Libraries**:
   - Include: `fastapi`, `uvicorn`, `pdfplumber`, `spacy`, `beautifulsoup4`, `requests`, `scikit-learn`, `sqlalchemy` (optional for database), `pydantic`, `aiohttp` (for async scraping), `celery`, `redis`, `python-multipart`.
   - Install spacy model: `python -m spacy download en_core_web_sm`.

7. **Additional Considerations**:
   - Avoid local file storage; process files in memory.
   - Include basic error handling (e.g., invalid file types, scraping failures).
   - Suggest using a database (e.g., PostgreSQL with SQLAlchemy) for production to store job matches.
   - Provide instructions for running the FastAPI server and Celery worker.

## Deliverables

- Sample code snippets for:
  - FastAPI app (`main.py`) with endpoints.
  - Celery task (`tasks.py`) for resume parsing, scraping, and matching.
  - Pydantic models (`models.py`) for API responses.
- List of required libraries and setup instructions (e.g., Redis, Celery worker).
- Brief explanation of the directory structure.

## Constraints

- Do not include frontend code or references to React/Tailwind.
- Focus on backend logic only.
- Keep snippets concise, illustrating structure without full implementation.
- Ensure compatibility with asynchronous processing and production environments.

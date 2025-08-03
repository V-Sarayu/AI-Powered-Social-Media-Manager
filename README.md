# AI-Powered Social Media Manager

A unified platform designed for college clubs and organizations to automate social media marketing using AI and real-time trend data.

## Features

- Trend scraping from Instagram and YouTube using official APIs
- AI-generated content using Google Gemini LLM with club-specific context via Retrieval-Augmented Generation (RAG)
- Auto-generation of branded, downloadable event posters in multiple styles
- PostgreSQL-based logging and analysis of trending topics
- Streamlit-based user interface for interactive input and output
- Environment variable-based security for API keys and database credentials

## Project Structure

```
AI-Powered-Social-Media-Manager/
├── app.py
├── backend/
│   ├── scraping/
│   │   ├── instagram_scraper.py
│   │   └── youtube_scraper.py
│   ├── poster/
│   │   └── poster.py
│   ├── updated_company_rag.py
│   ├── integrated-social-media-content-generator.py
│   ├── integrated_json_rag.py
│   ├── autosocial_llm_generator.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   ├── create_tables.py
│   └── rag/
│       ├── chroma_setup.py
│       ├── retriever.py
│       ├── test_query.py
│       └── club_data/
│           └── club_info.txt
├── data/
│   └── company_details.json
├── designed_posters/
│   ├── Hacknight_poster_style1.png
│   ├── Hacknight_poster_style2.png
│   ├── Hacknight_poster_style3.png
│   └── Hacknight_poster_style4.png
├── storage/
│   ├── docstore.json
│   ├── graph_store.json
│   ├── image__vector_store.json
│   └── index_store.json
├── hashtags.csv
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```



## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AI-Powered-Social-Media-Manager.git
   cd AI-Powered-Social-Media-Manager
   ```

2. **Create a Python virtual environment and install dependencies**
   ```bash
   python -m venv venv
   ```

   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```

   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

   - Then install:
     ```bash
     pip install -r requirements.txt
     ```

3. **Create a `.env` file**

   Add the following to `.env` in the root directory:
   ```env
   APIFY_API_KEY=your_apify_key
   YOUTUBE_API_KEY=your_youtube_data_api_key
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=postgresql://postgres:password@localhost:5432/autosocial
   ```

4. **Add club metadata**

   Create `data/company_details.json` with your club details:
   ```json
   {
     "name": "CodeCrafters",
     "about": "A club for tech and coding enthusiasts.",
     "logo_url": "logo.png",
     "services": "Workshops, hackathons, fun coding events.",
     "keywords": ["python", "coding", "ai"],
     "tone": "Friendly, professional"
   }
   ```

5. **Set up PostgreSQL**

   - Install PostgreSQL and create a database named `autosocial`.
   - Ensure `DATABASE_URL` in your `.env` points to this database.
   - Run the setup script:
     ```bash
     python backend/create_tables.py
     ```

6. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

   Then visit the link shown in your terminal (typically [http://localhost:8501](http://localhost:8501)).


## API Key Requirements
Apify API Key (for Instagram scraping): Obtain from Apify

YouTube Data API Key: Obtain from Google Cloud Console

Gemini API Key: Obtain from Google AI Studio

Do not commit these keys. Always store them securely in your .env file.

## Security Notes
Never commit .env or any files containing secrets.

If secrets are accidentally pushed, refer to GitHub's secret scanning documentation and rotate your keys immediately.

## Customization
Club metadata: data/company_details.json

Poster styles: backend/poster/poster.py
Extend scrapers or add new ones: backend/scraping/

Add RESTful APIs: Extend via FastAPI inside backend/

## Troubleshooting
Blank Streamlit page: Check terminal for errors and ensure .env and company_details.json are correctly configured.

API errors: Verify API keys, quotas, and internet connection.

Push rejected due to secrets: Remove secrets from all commits, clean history, rotate keys, and force-push if necessary.

## Contribution
Contributions are welcome. Please open issues or submit pull requests for improvements or bug fixes.

Do not include API keys or secrets in any code submissions.

## License
This project is licensed under the MIT License.

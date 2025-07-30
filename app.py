import streamlit as st
from backend.scraping.instagram_scraper import scrape_instagram
from backend.scraping.youtube_scraper import get_trending_reels
from backend.updated_company_rag import CompanyRAG
from backend.poster.poster import generate_poster


st.set_page_config(page_title="AutoSocial Club Generator", layout="wide")
st.title(" Personalized Social Media Content Generator")

# Initialize RAG with company data
rag = CompanyRAG()

with st.form("event_form"):
    st.header("Enter Event Details")
    event_name = st.text_input("Event Name", "")
    event_about = st.text_area("What is the event about?", "")
    event_date = st.text_input("Event Date", "")
    event_time = st.text_input("Event Time", "")
    event_venue = st.text_input("Event Venue", "")
    hashtags = st.text_input("Extra Instagram topics (comma-separated)", "")
    submitted = st.form_submit_button("Generate Content")

if submitted:
    if not event_name.strip() or not event_about.strip():
        st.error("Please enter both Event Name and Event Description.")
    else:
        event = {"name": event_name, "about": event_about, "date": event_date, "time": event_time, "venue": event_venue}
        with st.spinner("Scraping Instagram and YouTube for trends..."):
            insta_tags = scrape_instagram(
                [h.strip() for h in hashtags.split(",") if h.strip()] + event_about.split()
            )
            yt_trends = get_trending_reels(event_about or event_name)
        st.success(f"Found {len(insta_tags)} Instagram hashtags & {len(yt_trends)} YouTube trends.")

        with st.spinner("Generating social media ideas with club info and trends..."):
            content = rag.generate_content(event, insta_tags, yt_trends)

        st.subheader(" AI-Generated Social Media Content")
        st.write(content)

        st.subheader(" Posters (choose a style and download)")
        cols = st.columns(4)
        for style, col in enumerate(cols, 1):
            poster_path = generate_poster(event, rag.company_info, style)
            with col:
                st.image(poster_path, caption=f"Style {style}")
                with open(poster_path, "rb") as f:
                    st.download_button(f"Download Style {style}", f, file_name=f"{event_name}_poster_style{style}.png")

import streamlit as st
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # PyMuPDF
import io

# Function to fetch course description from a catalog URL using a course code
def fetch_course_description(catalog_url, course_code):
    try:
        response = requests.get(catalog_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        # Normalize and search for course code
        course_code = course_code.upper().replace(" ", "")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if course_code in line.replace(" ", ""):
                # Return a few lines around the match
                snippet = " ".join(lines[i:i+5])
                return snippet.strip()
        return "Course code not found in catalog."
    except Exception as e:
        return f"Error fetching course: {e}"

# Function to compare two course descriptions
def compare_descriptions(desc1, desc2):
    try:
        vectorizer = TfidfVectorizer().fit_transform([desc1, desc2])
        similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]
        return round(similarity * 100, 2)
    except:
        return 0.0

# Function to generate a PDF report
def generate_pdf_report(course1, desc1, course2, desc2, similarity):
    buffer = io.BytesIO()
    doc = fitz.open()
    page = doc.new_page()
    text = f"Course 1: {course1}\n\nDescription:\n{desc1}\n\n"
    text += f"Course 2: {course2}\n\nDescription:\n{desc2}\n\n"
    text += f"Similarity Score: {similarity}%"
    page.insert_text((72, 72), text, fontsize=11)
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Course Equivalency Finder")

st.markdown("Enter the **catalog URLs** and **course codes** for two institutions:")

col1, col2 = st.columns(2)

with col1:
    url1 = st.text_input("Institution 1 Catalog URL")
    code1 = st.text_input("Institution 1 Course Code (e.g., CSE110)")

with col2:
    url2 = st.text_input("Institution 2 Catalog URL")
    code2 = st.text_input("Institution 2 Course Code (e.g., ICS31)")

if st.button("Compare Courses"):
    if url1 and code1 and url2 and code2:
        desc1 = fetch_course_description(url1, code1)
        desc2 = fetch_course_description(url2, code2)
        similarity = compare_descriptions(desc1, desc2)

        st.subheader("Results")
        st.markdown(f"**{code1} Description:** {desc1}")
        st.markdown(f"**{code2} Description:** {desc2}")
        st.markdown(f"**Similarity Score:** {similarity}%")

        pdf = generate_pdf_report(code1, desc1, code2, desc2, similarity)
        st.download_button("Download PDF Report", data=pdf, file_name="course_equivalency_report.pdf", mime="application/pdf")
    else:
        st.warning("Please fill in all fields.")

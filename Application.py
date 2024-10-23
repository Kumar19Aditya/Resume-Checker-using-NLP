import streamlit as st
import fitz  # PyMuPDF
import docx
import pickle
import re
import os
import base64
import nltk

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Load models
clf = pickle.load(open('clf.pkl', 'rb'))
tfidf = pickle.load(open('tfidf.pkl', 'rb'))

# Function to read PDF files
import fitz  # PyMuPDF

def read_pdf(uploaded_file):
    try:
        # Open the uploaded PDF file directly from the Streamlit 'BytesIO' object
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        st.error(f"An error occurred while reading the PDF: {e}")
        return ""

# Function to read DOCX files
def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

# Function to clean the resume text
def clean_resume(resume_text):
    clean_text = re.sub('http\\S+\\s*', ' ', resume_text)  # Note the double backslashes
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\\S+', '', clean_text)
    clean_text = re.sub('@\\S+', ' ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)
    clean_text = re.sub('\\s+', ' ', clean_text)  # Note the double backslash
    return clean_text

# Rest of your code remains the same...

# Map predicted ID to job category
category_mapping = {
    15: "Java Developer", 23: "Testing", 8: "DevOps Engineer", 20: "Python Developer",
    24: "Web Designing", 12: "HR", 13: "Hadoop", 3: "Blockchain",
    10: "ETL Developer", 18: "Operations Manager", 6: "Data Science", 22: "Sales",
    16: "Mechanical Engineer", 1: "Arts", 7: "Database", 11: "Electrical Engineering",
    14: "Health and Fitness", 19: "PMO", 4: "Business Analyst", 9: "DotNet Developer",
    2: "Automation Testing", 17: "Network Security Engineer", 21: "SAP Developer",
    5: "Civil Engineer", 0: "Advocate"
}

# Function to convert an image to base64
def image_to_base64(image_file):
    if os.path.exists(image_file):  # Check if the image file exists
        with open(image_file, "rb") as img:
            return base64.b64encode(img.read()).decode()
    else:
        st.error("Image file not found. Please check the path.")
        return None

# Custom CSS for better styling
bg_image = image_to_base64("Resume-Scanning-FB.png")  # Load your local image file
if bg_image:  # Proceed only if the image is successfully converted
    st.markdown(f"""
        <style>
        body {{
            background-image: url('data:image/jpeg;base64,{bg_image}'); 
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Arial';
            color: #333;
        }}
        .stButton button {{
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px;
            transition: background-color 0.3s;
        }}
        .stButton button:hover {{
            background-color: #45a049;
        }}
        .stTextInput input {{
            border-radius: 5px;
            padding: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Streamlit App
def main():
    st.title("📄 Resume Screening App")

    # User selects the desired job category
    selected_category = st.selectbox("Select Your Desired Job Category", list(category_mapping.values()))

    # Upload resume
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])

    if uploaded_file is not None:
        # Extract resume text
        if uploaded_file.name.endswith(".pdf"):
            resume_text = read_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            resume_text = read_docx(uploaded_file)

        # Clean and predict category
        cleaned_resume = clean_resume(resume_text)
        input_features = tfidf.transform([cleaned_resume])
        prediction_id = clf.predict(input_features)[0]

        # Get predicted category name
        predicted_category = category_mapping.get(prediction_id, "Unknown")

        # Display predicted job category
        st.subheader("Predicted Job Category")
        st.write(f"**{predicted_category}**")

        # Compare with selected category and display result
        if predicted_category == selected_category:
            st.success("✅ Match! Your resume aligns with the desired job category.")
        else:
            st.error("❌ Don't Match! Your resume does not align with the desired job category.")
    else:
        st.info("Please upload a PDF or DOCX resume to proceed.")

if __name__ == "__main__":
    main()

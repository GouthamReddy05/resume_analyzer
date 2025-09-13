import io
import pdfplumber
from pdfminer.high_level import extract_text

from huggingface_hub import InferenceClient

client = InferenceClient()


import io
import pdfplumber

def extract_ordered_text_pdf(file_input):
    """
    Extract text from PDF using pdfplumber.
    Works with:
      - File path (string)
      - File-like object (Flask upload)
    """
    # If it's a file-like object (has .read)
    if hasattr(file_input, "read"):
        file_bytes = file_input.read()
        file_input.seek(0)  # reset pointer
        pdf_source = io.BytesIO(file_bytes)
    else:
        # Assume it's a file path (string)
        pdf_source = file_input

    text = ""
    with pdfplumber.open(pdf_source) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text




# print(extract_ordered_text_pdf("Resume.pdf"))

def send_text_to_llm(text):
    
    prompt = f"""
    You are an AI that organizes resume text into structured sections.

    Task:
    - Organize the resume text into these exact sections:
      - Name and Contact Information
      - Introduction/Summary
      - Experience
      - Projects
      - Education
      - Skills
      - Certifications
    - If a section uses a different title (e.g., "Profile", "Career Overview"), map it to the most relevant one.
    - If any section is missing, still include it with an empty string ("").

    Input Resume Text:
    {text}

    Output:
    Return ONLY valid JSON in this format:
    {{
      "Name and Contact Information": "",
      "Introduction/Summary": "",
      "Experience": "",
      "Projects": "",
      "Education": "",
      "Skills": "",
      "Certifications": ""
    }}
    """


    try:
        response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response.choices[0].message.content}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    

def retrieve_skills(text):
    prompt = f"""
    You are an AI career assistant.
    Task: you are given a resume text. Extract and list all the skills mentioned in the resume in a correct order.
    Input: {text}
    Output: A list of skills in JSON format and do not seperate combine all types of skills into list with numbering without double quotes.
    """
    try:
        response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response.choices[0].message.content}"
    
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    

def generate_missing_skills(role, candidate_skills):
    prompt = f"""
    You are an AI career assistant.

    Task:
    1. Analyze the target job role and list essential skills required.
    2. Compare those required skills with the candidate's skills.
    3. Identify the missing skills which are essential for the given role (avoid adding unnecessary skills).
    4. Return only the missing skills in JSON format under these categories:
       - Core Technical Skills
       - Programming Languages/Frameworks
       - Tools & Platforms
    Note: Just output the missing skills.

    Input:
    Role: "{role}"
    Candidate Skills: {candidate_skills}

    Output:
    {{
      "Core Technical Skills": [],
      "Programming Languages/Frameworks": [],
      "Tools & Platforms": []
    }}
    """


    try:
        response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response.choices[0].message.content}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



# text = extract_ordered_text_pdf("Resume.pdf")
# # print(text)

# structured_text = send_text_to_llm(text)
# # print(structured_text)

# skills = retrieve_skills(structured_text)
# # print(skills)

# missing_skills = generate_missing_skills("Machine Learning engineer", skills)
# print(missing_skills)

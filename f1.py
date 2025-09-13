import pdfplumber
import ollama

def extract_ordered_text_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# print(extract_ordered_text_pdf("Resume.pdf"))



def send_text_to_llm(text):
    
    prompt = """

Organize the resume text into these sections:
- Name and Contact Information
- Introduction/Summary
- Experience
- Projects
- Education
- Skills
- Certifications

If a section uses a different title (e.g., "Profile", "Career Overview"), map it to the most relevant section. If at all relevant sessions are missing, give the same name and map it.

Return the result as JSON with only these exact section names.

input text: {text}

Output JSON:"""

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    

def extract_keywords(job_description):
    prompt = f"""
    You are an AI career assistant.
    Task: you are given a resume text. Extract and list all the keywords relevant for the job role.
    Input: {job_description}
    Output: A list of keywords in JSON format.
    """
    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



def generate_missing_skills(role, candidate_skills):
    
    prompt = f"""
    You are an AI career assistant.

    Task:
    1. Analyze the target job role and list essential skills required.
    2. Compare those required skills with the candidate's skills.
    3. Identify missing skills.
    4. Return only the missing skills in JSON format under these categories:
    - Core Technical Skills
    - Programming Languages/Frameworks
    - Tools & Platforms
    - Soft Skills

    Input:
    Role: "{role}"
    Candidate Skills: {candidate_skills}

    Output:
    {{
    "Core Technical Skills": [...],
    "Programming Languages/Frameworks": [...],
    "Tools & Platforms": [...],
    "Soft Skills": [...]
    }}
    """

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



def retrieve_skills(text):
    prompt = f"""
    You are an AI career assistant.
    Task: you are given a resume text. Extract and list all the skills mentioned in the resume in a correct order.
    Input: {text}
    Output: A list of skills in JSON format.
    """
    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


def ats_score_generator(skills, job_description):
    prompt = f"""
    You are an expert in Applicant Tracking Systems (ATS) and resume optimization.

    Task:
    1. Analyze the provided resume text against the job description.
    2. Identify key skills, experiences, and keywords from the job description.
    3. Compare these with the resume content.
    4. Calculate an ATS compatibility score (0-100) based on keyword matches, relevant experience, and formatting.
    5. Provide a brief explanation of the score.

    Input:
    Resume Text: "{skills}"
    Job Description: "{job_description}"

    Output:
    {{
    "ATS Score": <score>,
    "Explanation": "<brief explanation>"
    }}
    """

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    




def generate_project_ideas(role, job_description):
    prompt = f"""
    You are an AI career assistant that helps candidates strengthen their resume by suggesting real-world project ideas.

    Job Role: {role}
    Job Description: {job_description} 

    Your task:
    1. Analyze the role and job description.
    2. Identify the most critical skills and tools required for success in this role.
    3. Suggest 5 practical project ideas that a candidate can work on to demonstrate these skills.
    4. For each time generate different project ideas.
    Note: if job description is not provided, infer the skills based on the job role.

    For each project, provide:
    - Project Title (short & impactful)
    - Objective (what problem it solves or simulates)
    - Tools/Technologies (languages, frameworks, platforms to use)
    - Skills Demonstrated (specific technical & soft skills)
    - Resume Impact (how adding this project will make the resume stronger for this job role)

    """

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



def generate_interview_questions(role, skills):

    combined_prompt = """You are an expert AI interview question generator. Based on the following prompt categories, generate relevant questions accordingly:

1. DSA and Core CS Concepts:
Generate a list of the most important and frequently asked Data Structures and Algorithms (DSA) questions along with core Computer Science fundamentals (like DBMS, Computer Networks, Operating Systems, and OOPs). The questions should be focused on efficiency, real-world problem solving, and conceptual depth. Make sure the questions are relevant to the role and suitable for interview preparation and no overlapping of concepts should be done.

2. Technical Skills:
Generate efficient and role-relevant interview questions based on the following technical skills: {skills}, etc. The questions should evaluate practical experience, project understanding, design thinking, and problem-solving related to these skills.

3. Role-Specific Scenarios:
Generate technical and scenario-based interview questions specifically for the job role of [ROLE_NAME]. Focus on real-world challenges, problem-solving, and domain-specific skills. Include both conceptual and practical questions expected in interviews for this role.

4. HR Interview:
Generate a list of common and insightful HR interview questions that assess candidate motivation, soft skills, long-term goals, cultural fit, and behavioral traits. Include standard questions like “Where do you see yourself in 5 years?” and others commonly asked in HR rounds. Focus on questions that help understand the candidate's personality, work ethic, and alignment with company values.

Note: Generate different questions each time for the same role and skills which are important.

Give 5 questions under each category which should be efficient.
Return the output in JSON format with the following structure:
{{
    "DSA_and_Core_CS": [ ... 5 questions ... ],
    "Technical_Skills": [ ... 5 questions ... ],
    "Role_Specific": [ ... 5 questions ... ],
    "HR": [ ... 5 questions ... ]
}}

"""
    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_prompt}
        ])

        return f"{response['message']['content']}"  
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



ans = generate_interview_questions("Data Scientist", "Python, Machine Learning, Data Analysis")
print(ans)

# ans = generate_project_ideas("Data Analyst", "")
# print(ans)

# print(llm_response)



# print(extract_keywords("Machine Learning Engineer"))
# data = extract_ordered_text_pdf("Resume.pdf")

# llm_response = send_text_to_llm(data)

# skills = retrieve_skills(data)
# print(skills)

# role = "Machine Learning Engineer"
# print(ats_score_generator(skills, role))

# candidate_skills = ["Python", "Machine Learning", "Data Analysis"]

# missing_skills = generate_missing_skills(role, candidate_skills)

# print(missing_skills)








##Adzuna API-------------------------------------------------------

## I want to build an AI Agent that can fetch job listings from Adzuna API based on user queries and preferences.
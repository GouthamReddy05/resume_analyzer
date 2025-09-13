import ollama
from huggingface_hub import InferenceClient

client = InferenceClient()

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
    Note: use numbered list for project ideas and just give what i mentioned in the prompt and No extra explanations, no stars, no extra formatting

    For each project, provide:
    - Project Title (short & impactful)
    - Objective (what problem it solves or simulates)
    - Tools/Technologies (languages, frameworks, platforms to use)
    - Skills Demonstrated (specific technical & soft skills)

    """

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat_completion(
            messages=messages,
            model="openai/gpt-oss-120b"
        )

        return f"{response.choices[0].message.content}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# print(generate_project_ideas("Data Scientist", "Experience with Python, Machine Learning, Data Analysis, and statistical modeling."))
from huggingface_hub import InferenceClient


client = InferenceClient()


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

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat_completion(
            messages=messages,
            model="meta-llama/Llama-3.3-70B-Instruct"
        )

        return f"{response.choices[0].message.content}"  
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
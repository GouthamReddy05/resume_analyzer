from huggingface_hub import InferenceClient


client = InferenceClient()

def generate_interview_questions(role, skills):

    combined_prompt = """
You are an expert AI interview question generator. Based on the given job role and technical skills, generate relevant interview questions in four categories.

Categories and Instructions:

1. DSA_and_Core_CS questions:
Generate 5 important and frequently asked questions from Data Structures and Algorithms (DSA) and Core CS fundamentals (DBMS, Computer Networks, Operating Systems, OOPs). 
Focus on efficiency, problem-solving, and conceptual depth. No overlap.

2. Technical_Skills questions:
Generate 5 role-relevant technical interview questions from all the provided skills combined (not 5 per skill). 
These should focus on practical experience, project understanding, design thinking, and problem-solving.

3. Role_Specific questions:
Generate 5 interview questions specifically for the given job role. 
Questions should be scenario-based, technical, and related to real-world challenges for this role.

4. HR Round questions:
Generate 5 HR interview questions to assess motivation, personality, work ethic, goals, and cultural fit. 
Include standard and behavioral questions.

Important:
- Always generate different questions for the same input. 
- Return the result strictly in JSON format:
{
    "DSA and Core CS questions": [1. , 2. , 3. , 4. , 5. ],
    "Technical_Skills questions": [1. , 2. , 3. , 4. , 5. ],
    "Role Specific questions": [1. , 2. , 3. , 4. , 5. ],
    "HR Round questions": [1. , 2. , 3. , 4. , 5. ]
}
"""


    messages = [
        {"role": "user", "content": combined_prompt}
    ]

    try:
        response = client.chat_completion(
            messages=messages,
            model="meta-llama/Llama-3.3-70B-Instruct"
        )

        return f"{response.choices[0].message.content}"  
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


# print(generate_interview_questions("Data Scientist", "Python, Machine Learning, Data Analysis"))

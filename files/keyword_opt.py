from huggingface_hub import InferenceClient

client = InferenceClient() 

prompt = "DSA and Core CS Concepts: Generate a list of the most important and frequently asked Data Structures and Algorithms (DSA) questions along with core Computer Science fundamentals (like DBMS, Computer Networks, Operating Systems, and OOPs). The questions should be focused on efficiency, real-world problem solving, and conceptual depth. Make sure the questions are relevant to the role and suitable for interview preparation and no overlapping of concepts should be done."

messages = [
    {"role": "user", "content": prompt}
]

response = client.chat_completion(
    messages=messages,
    model="mistralai/Mistral-7B-Instruct-v0.2"
)

# print(response.choices[0].message.content)
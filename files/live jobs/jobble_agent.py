from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
from langchain_community.llms import Ollama
import requests
from dotenv import load_dotenv
import os
import re


load_dotenv()

JOOBLE_API_KEY = os.getenv("jobble_api_key")

@tool
def fetch_jobs_from_jooble(role_location: str) -> str:
    """
    Fetch job listings from Jooble API based on role and location.
    Returns a formatted string with job titles, companies, locations, and links.
    """
    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = ""
    
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

    headers = {"Content-type": "application/json"}
    payload = {"keywords": role, "location": location, "page": 1, "jobs_per_page": 5}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return f"❌ Error: {response.status_code} {response.reason}"
    
    jobs = response.json().get("jobs", [])
    if not jobs:
        return "No jobs found."
    
    result_text = ""
    for job in jobs:
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        loc = job.get("location", "N/A")
        link = job.get("link", "#")
        result_text += f"🔹 {title} – {company}\n📍 {loc}\n🔗 {link}\n\n"
    
    return result_text.strip()


# Initialize LLM
llm = Ollama(model="llama3")

tools = [fetch_jobs_from_jooble]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True
)

# Run agent
role_location = "Software Developer, India"
response = agent.invoke(role_location)


# Extract and print only the job links from the output
if isinstance(response, dict) and 'output' in response:
    output_text = response['output']
else:
    output_text = str(response)
links = re.findall(r'https?://[^\s]+', output_text)
print("\nJob Links:")
for link in links:
    print(link)

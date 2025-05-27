from together import Together
import re  # For URL detection
import requests  # For fetching HTML in workflow1

client = Together()  # auth defaults to os.environ.get("TOGETHER_API_KEY")

ROUTER_AGENT_PROMPT_TEMPLATE = """You are an intelligent assistant in a multi-agent real estate analysis system.

Your task is to classify a user's query into one of two types:

1. **q1 (Link query):** The user includes a specific URL to a real estate listing (e.g., unegui.mn or 1212.mn or remax.mn)
2. **q2 (General interest query):** The user is generally interested in a location or type of apartment but does not include a specific link.

Based on the input, respond only with one of these options:  
→ `q1` if the input contains a real estate listing URL  
→ `q2` if it describes a type of property or location but doesn't have a URL  

Do not explain your reasoning. Output only `q1` or `q2`.

---

Input: {user_query}
Output:"""

def classify_query(user_query: str, llm_client: Together) -> str:
    """
    Classifies the user query as 'q1' or 'q2' using the RouterAgent.
    """
    url_pattern = re.compile(r'https?://(?:www\.)?(unegui\.mn|1212\.mn|remax\.mn)[^\s]*', re.IGNORECASE)
    if url_pattern.search(user_query):
        pass

    prompt = ROUTER_AGENT_PROMPT_TEMPLATE.format(user_query=user_query)
    
    try:
        response = llm_client.chat.completions.create(
            model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=5
        )
        classification = response.choices[0].message.content.strip().lower()
        if classification in ['q1', 'q2']:
            return classification
        else:
            print(f"Warning: LLM returned unexpected classification: {classification}")
            return 'q1' if url_pattern.search(user_query) else 'q2'
    except Exception as e:
        print(f"Error during LLM call for classification: {e}")
        return 'q1' if url_pattern.search(user_query) else 'q2'

def workflow1_retriever(url: str) -> str:
    """
    Workflow 1: Retriever - Fetches HTML content from the URL.
    """
    print(f"Workflow 1 (Retriever): Fetching content from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text 
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return f"Error: Could not retrieve content from {url}."

def workflow1_researcher(html_content: str) -> str:
    """
    Workflow 1: Researcher - Processes HTML content to extract relevant information.
    """
    print("Workflow 1 (Researcher): Analyzing retrieved content...")
    return f"Analyzed content (length: {len(html_content)} characters)."

def workflow1_writer(context: str) -> str:
    """
    Workflow 1: Writer - Generates the final report from the context.
    """
    print("Workflow 1 (Writer): Generating report...")
    return f"Final Report (from URL):\n{context}"

def workflow2_researcher(query_text: str) -> str:
    """
    Workflow 2: Researcher - Gathers information based on the general query.
    """
    print(f"Workflow 2 (Researcher): Researching general query: '{query_text}'")
    return f"Context gathered for general query: '{query_text}' (Details TBD)."

def workflow2_writer(context: str) -> str:
    """
    Workflow 2: Writer - Generates the final report from the context.
    """
    print("Workflow 2 (Writer): Generating report...")
    return f"Final Report (from general query):\n{context}"

def main():
    user_query = input("Please enter your real estate query (e.g., a URL or a description): ")

    query_type = classify_query(user_query, client)
    print(f"Query classified as: {query_type}")

    final_report = ""

    if query_type == 'q1':
        url_match = re.search(r'https?://[^\s]+', user_query)
        if url_match:
            url = url_match.group(0)
            print(f"Detected URL: {url}")
            html_content = workflow1_retriever(url)
            if not html_content.startswith("Error:"):
                research_context = workflow1_researcher(html_content)
                final_report = workflow1_writer(research_context)
            else:
                final_report = html_content
        else:
            final_report = "Error: q1 classification but no URL found in the query."
            print(final_report)
    elif query_type == 'q2':
        research_context = workflow2_researcher(user_query)
        final_report = workflow2_writer(research_context)
    else:
        final_report = "Error: Could not classify the query."
        print(final_report)

    print("\n--- Generated Report ---")
    print(final_report)
    print("--- End of Report ---")

if __name__ == "__main__":
    main()
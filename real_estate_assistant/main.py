# real_estate_assistant/main.py

from agents.router import RouterAgent
from agents.retriever import RetrieverAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
# from utils import load_config, setup_llm_client # Example utility functions
# from generate_pdf import create_pdf_report # If PDF generation is separate

# Placeholder for LLM client initialization (e.g., Together)
# from together import Together
# llm_client = Together() # Ensure API key is configured

class MockLLMClient: # Replace with your actual LLM client
    def chat_completions_create(self, model, messages, max_tokens=150):
        # Simulate LLM response
        class Choice:
            def __init__(self, text):
                self.message = type('obj', (object,), {'content': text})
        class MockResponse:
            def __init__(self, choices):
                self.choices = choices
        
        # Basic mock logic for router
        if "Output:" in messages[0]['content']: # Router prompt
             if "http" in messages[0]['content'] and "unegui.mn" in messages[0]['content']:
                return MockResponse([Choice("q1")])
             else:
                return MockResponse([Choice("q2")])
        # Basic mock logic for researcher/writer (very simplified)
        return MockResponse([Choice("Mocked LLM response based on input.")])

llm_client = MockLLMClient() # Use the mock client for now

def run_workflow1(user_query: str, retriever: RetrieverAgent, researcher: ResearcherAgent, writer: WriterAgent):
    """
    Workflow for handling queries with a specific URL.
    """
    print("\n--- Starting Workflow 1 (URL Query) ---")
    # A more robust URL extraction might be needed if the query isn't just the URL
    url = user_query # Assuming user_query is primarily the URL for simplicity here
    
    # 1. Retriever fetches HTML
    html_content = retriever.fetch_listing_data(url)
    if html_content.startswith("Error:"):
        print(html_content)
        return html_content

    # (Optional) Save raw HTML
    # with open(f"data/raw_listings/{url.split('/')[-1]}.html", "w", encoding="utf-8") as f:
    #     f.write(html_content)

    # 2. Researcher analyzes HTML
    listing_details = researcher.analyze_listing_html(html_content, url)
    
    # (Optional) Researcher performs broader market context research
    # For a single URL, this might involve finding comparables.
    # This part is more complex and might need its own sub-flow.
    # For now, we'll pass minimal data to market research.
    market_analysis_context = researcher.research_market_data(
        processed_listings_data=[listing_details] # Simplified
    )

    # 3. Writer generates report
    report_text = writer.generate_report_text(
        analysis_data=market_analysis_context,
        listing_details=listing_details
    )
    final_report = writer.create_final_report(report_text, output_format="text") # or "pdf"
    
    print("--- Workflow 1 Completed ---")
    return final_report

def run_workflow2(user_query: str, retriever: RetrieverAgent, researcher: ResearcherAgent, writer: WriterAgent):
    """
    Workflow for handling general interest queries.
    """
    print("\n--- Starting Workflow 2 (General Query) ---")
    # 1. Retriever searches for listings based on query (e.g., location, type)
    # This needs parsing the user_query to extract criteria
    # For simplicity, we'll use placeholder criteria
    # In a real app, use NLP or structured input for these.
    print(f"Interpreting general query: {user_query}")
    # Mock criteria extraction:
    location = "Ulaanbaatar"
    property_type = "apartment"
    if "house" in user_query.lower():
        property_type = "house"
    if "bayanzurkh" in user_query.lower():
        location = "Bayanzurkh district"
        
    general_listings_data = retriever.search_general_listings(
        location=location, 
        property_type=property_type
        # Potentially add more criteria extracted from user_query
    )

    if not general_listings_data:
        message = "No listings found matching your general query."
        print(message)
        return message

    # 2. Researcher processes these listings and performs market analysis
    # This might involve fetching details for each found listing if not already done by retriever
    processed_data_for_research = []
    for item in general_listings_data:
        # If retriever only returns summaries, fetch full details if needed
        # html_content = retriever.fetch_listing_data(item['url'])
        # details = researcher.analyze_listing_html(html_content, item['url'])
        # processed_data_for_research.append(details)
        # For this skeleton, assume retriever provides enough info or researcher works with summaries
        processed_data_for_research.append({
            "url": item.get("url"),
            "title": item.get("title"),
            "price": item.get("price"),
            # Add other relevant fields if search_general_listings provides them
        })


    market_analysis = researcher.research_market_data(
        processed_listings_data=processed_data_for_research,
        general_query_info={"query": user_query, "location": location, "property_type": property_type}
    )

    # 3. Writer generates report
    report_text = writer.generate_report_text(analysis_data=market_analysis)
    final_report = writer.create_final_report(report_text, output_format="text") # or "pdf"
    
    print("--- Workflow 2 Completed ---")
    return final_report

def main():
    # Initialize agents
    router = RouterAgent(llm_client=llm_client)
    retriever = RetrieverAgent()
    researcher = ResearcherAgent(llm_client=llm_client) # Pass LLM client if researcher uses it
    writer = WriterAgent(llm_client=llm_client) # Pass LLM client if writer uses it

    user_query = input("Welcome to the Real Estate Assistant!\nPlease enter your query (e.g., a property URL or a general description like 'apartments in Khan-Uul'):\n> ")

    query_type = router.classify_query(user_query)
    print(f"Query classified as: {query_type}")

    final_report = ""
    if query_type == 'q1':
        # A simple way to extract URL if query_type is q1 and query contains it.
        # More robust URL extraction might be needed.
        import re
        url_match = re.search(r'https?://(?:www\.)?(unegui\.mn|1212\.mn|remax\.mn)[^\s]*', user_query, re.IGNORECASE)
        if url_match:
            url = url_match.group(0)
            final_report = run_workflow1(url, retriever, researcher, writer)
        else:
            final_report = "Error: Classified as q1, but no valid real estate URL found in the query."
            print(final_report)
            
    elif query_type == 'q2':
        final_report = run_workflow2(user_query, retriever, researcher, writer)
    else:
        final_report = "Error: Could not reliably classify the query."
        print(final_report)

    print("\n========== FINAL REPORT ==========")
    print(final_report)
    print("================================")

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    import os
    os.makedirs("data/raw_listings", exist_ok=True)
    os.makedirs("data/processed_data", exist_ok=True)
    os.makedirs("vectorstore/faiss_index", exist_ok=True)
    os.makedirs("prompts", exist_ok=True) # If prompts dir is at top level of assistant
    
    main()

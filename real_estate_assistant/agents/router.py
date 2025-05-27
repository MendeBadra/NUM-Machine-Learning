# real_estate_assistant/agents/router.py

# Placeholder for imports (e.g., from together import Together, re)

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

class RouterAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        # Consider pre-compiling regex patterns here if used frequently
        # self.url_pattern = re.compile(r'https?://(?:www\.)?(unegui\.mn|1212\.mn|remax\.mn)[^\s]*', re.IGNORECASE)


    def classify_query(self, user_query: str) -> str:
        """
        Classifies the user query as 'q1' or 'q2'.
        """
        # Basic check for URLs (optional, can rely solely on LLM)
        # if self.url_pattern.search(user_query):
        #     # Potentially optimize or inform the LLM
        #     pass

        prompt = ROUTER_AGENT_PROMPT_TEMPLATE.format(user_query=user_query)
        
        try:
            # Replace with actual LLM call logic
            # response = self.llm_client.chat.completions.create(...)
            # classification = response.choices[0].message.content.strip().lower()
            
            # Placeholder logic:
            if "http" in user_query and ("unegui.mn" in user_query or "1212.mn" in user_query or "remax.mn" in user_query) :
                classification = "q1"
            else:
                classification = "q2"
            
            if classification in ['q1', 'q2']:
                return classification
            else:
                # Fallback or error handling
                print(f"Warning: LLM returned unexpected classification: {classification}")
                # A simple fallback based on URL presence
                # return 'q1' if self.url_pattern.search(user_query) else 'q2'
                return 'q2' # Default fallback
        except Exception as e:
            print(f"Error during LLM call for classification: {e}")
            # Fallback mechanism
            # return 'q1' if self.url_pattern.search(user_query) else 'q2'
            return 'q2' # Default fallback

if __name__ == '__main__':
    # Example Usage (requires a mock or real LLM client)
    class MockLLMClient:
        def chat_completions_create(self, model, messages, max_tokens):
            # Simulate LLM response based on keywords for testing
            query_content = messages[0]['content']
            if "http" in query_content and "unegui.mn" in query_content:
                class Choice:
                    def __init__(self, text):
                        self.message = type('obj', (object,), {'content': text})
                class MockResponse:
                    def __init__(self, choices):
                        self.choices = choices
                return MockResponse([Choice("q1")])
            else:
                class Choice:
                    def __init__(self, text):
                        self.message = type('obj', (object,), {'content': text})
                class MockResponse:
                    def __init__(self, choices):
                        self.choices = choices
                return MockResponse([Choice("q2")])

    mock_client = MockLLMClient()
    router = RouterAgent(llm_client=mock_client)
    
    test_query_url = "Can you analyze this listing? http://unegui.mn/property/12345"
    test_query_general = "I'm looking for apartments in Ulaanbaatar near the city center."
    
    print(f"Query: '{test_query_url}' -> Classification: {router.classify_query(test_query_url)}")
    print(f"Query: '{test_query_general}' -> Classification: {router.classify_query(test_query_general)}")


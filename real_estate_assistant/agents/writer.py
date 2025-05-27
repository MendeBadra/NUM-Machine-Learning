# real_estate_assistant/agents/writer.py

import os
from langchain_together import ChatTogether

class WriterAgent:
    def __init__(self, model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo"):
        """
        Initializes the WriterAgent with Together's ChatTogether client.
        """
        self.api_key = os.getenv("TOGETHER_API_KEY", "your_together_api_key_here")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment variables.")
        self.llm = ChatTogether(
            together_api_key=self.api_key,
            model=model
        )
        print(f"WriterAgent: Initialized with model {model}")

    def generate_report(self, listing_details: dict, market_context: dict = None) -> str:
        """
        Generates a textual report using Together's LLM based on listing details and market context.
        """
        print("WriterAgent: Generating textual report...")

        if not listing_details:
            return "Error: No listing details provided to generate report."

        # Use placeholder market context if none is provided
        if market_context is None:
            market_context = {
                "listings_analyzed": 1,
                "average_price": "MNT 150,000,000 (Placeholder)",
                "price_range": "MNT 100,000,000 - MNT 200,000,000 (Placeholder)",
                "key_insights": [
                    "Market appears active for this type of property.",
                    "Prices vary based on location and condition (Placeholder)."
                ]
            }

        # Construct the prompt
        prompt = f"""
You are a real estate analyst. Your task is to generate a concise report.
Use the "Extracted Listing Details" and "Market Context" provided below to fill in the "[TO BE FILLED]" placeholders in the "Output Format".
If a detail in "Extracted Listing Details" is "N/A", use "N/A" in the corresponding "[TO BE FILLED]" part of the report.
Ensure the final output strictly adheres to the "Output Format".

Extracted Listing Details:
URL: {listing_details.get("url", "N/A")}
Title: {listing_details.get("title", "N/A")}
Price: {listing_details.get("price", "N/A")}
Location: {listing_details.get("location", "N/A")}
Area: {listing_details.get("area", "N/A sqm")}
Rooms: {listing_details.get("bedrooms", "N/A")}
Description: {listing_details.get("description", "N/A")}

Market Context:
Listings Analyzed: {market_context.get("listings_analyzed", "N/A")}
Average Price: {market_context.get("average_price", "N/A")}
Price Range: {market_context.get("price_range", "N/A")}
Key Insights:
{chr(10).join(f"- {insight}" for insight in market_context.get("key_insights", ["N/A"]))}

Output Format:
========== FINAL REPORT ==========
## Single Listing Analysis

**URL:** [TO BE FILLED - use URL from Extracted Listing Details]
**Title:** [TO BE FILLED - use Title from Extracted Listing Details]
**Price:** [TO BE FILLED - use Price from Extracted Listing Details]
**Location:** [TO BE FILLED - use Location from Extracted Listing Details]
**Area:** [TO BE FILLED - use Area from Extracted Listing Details, should include 'sqm' or be 'N/A sqm']
**Bedrooms:** [TO BE FILLED - use Bedrooms from Extracted Listing Details, or 'N/A']
**Description:** [TO BE FILLED - use Description from Extracted Listing Details]

## Market Context & Analysis

**Listings Analyzed:** [TO BE FILLED - use Listings Analyzed from Market Context]
**Average Price:** [TO BE FILLED - use Average Price from Market Context]
**Price Range:** [TO BE FILLED - use Price Range from Market Context]

**Key Insights:**
[TO BE FILLED - use Key Insights from Market Context, each on a new line starting with '- ']
================================
"""
        try:
            print("WriterAgent: Sending prompt to Together LLM...")
            # Changed from self.llm.chat to self.llm.invoke
            # The response structure from invoke is typically an AIMessage object
            # with a 'content' attribute.
            response = self.llm.invoke(prompt, max_tokens=1024, temperature=0.1)
            report_content = response.content  # Adjusted to access content directly
            print("WriterAgent: Report content received from LLM.")
            return report_content
        except Exception as e:
            print(f"WriterAgent: Error during LLM call: {e}")
            return f"Error: Could not generate report using LLM. Details: {e}"

if __name__ == '__main__':
    # Example usage of WriterAgent
    writer = WriterAgent()

    # Example data
    sample_listing_details = {
        "url": "https://www.unegui.mn/adv/9129580_tomor-zamd-2-oroo-zarna/",
        "title": "Төмөр замд 2 өрөө байр зарна",
        "price": "₮155,000,000",
        "location": "Улаанбаатар, Баянгол, 4-р хороо",
        "area": "56 sqm",
        "bedrooms": "2",
        "description": "Төмөр замд байрлалтай, бүрэн цутгамал, 2 өрөө байр зарна. Гал тогооны тавилга үлдэнэ."
    }

    sample_market_context = {
        "listings_analyzed": 5,
        "average_price": "MNT 160,000,000",
        "price_range": "MNT 140,000,000 - MNT 180,000,000",
        "key_insights": [
            "Similar 2-bedroom apartments in the area show consistent pricing.",
            "Demand for properties near Tomor Zam is relatively high."
        ]
    }

    print("\n--- Testing WriterAgent with sample data ---")
    report = writer.generate_report(sample_listing_details, sample_market_context)
    print("\nGenerated Report:")
    print(report)

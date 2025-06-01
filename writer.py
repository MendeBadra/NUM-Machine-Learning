import os
import pandas as pd
from langchain_together import ChatTogether
from build_index import build_vector_store
 
 
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
 
    def generate_report(self, listing_details: dict, market_context: dict = None, translate=False) -> str:
        """
        Generates a textual report based on listing details and market context.
        Optionally translates the report to Mongolian.
        """
        print("WriterAgent: Generating textual report...")
 
        if not listing_details:
            return "Error: No listing details provided to generate report."
 
        if market_context is None:
            market_context = {
                "listings_analyzed": 0,
                "average_price": "N/A",
                "key_insights": ["No market data available."]
            }
 
        prompt = f"""
You are a professional real estate analyst.
 
Your task is to analyze whether the following apartment listing is a good deal, using step-by-step reasoning based on the listing and the market data.
 
Use the following format:
1. Summarize the listing in 1–2 sentences.
2. Compare the listing's price and area to the market average.
3. Analyze the district/location and any other notable features.
4. Based on your reasoning, give a verdict: **"Good deal"**, **"Average deal"**, or **"Overpriced"** — and explain why.
 
Be specific and base your reasoning on numbers where possible.
 
---
 
**Apartment Listing Details:**
URL: {listing_details.get("url", "N/A")}
Title: {listing_details.get("title", "N/A")}
Price: {listing_details.get("price", "N/A")}
Location: {listing_details.get("location", "N/A")}
Area: {listing_details.get("area", "N/A sqm")}
Rooms: {listing_details.get("bedrooms", "N/A")}
Description: {listing_details.get("description", "N/A")}
 
**Market Context:**
Listings Analyzed: {market_context.get("listings_analyzed", "N/A")}
Average Price: {market_context.get("average_price", "N/A")}
Key Insights:
{chr(10).join(f"- {insight}" for insight in market_context.get("key_insights", ["N/A"]))}
 
---
 
Format:
========== MARKET ANALYSIS REPORT ==========
 
### Step-by-Step Reasoning
1. [Summary of the apartment.]
2. [Price vs market.]
3. [Location & other considerations.]
4. [Final verdict with justification.]
 
============================================
"""
 
        try:
            print("WriterAgent: Sending prompt to Together LLM...")
            response = self.llm.invoke(prompt, max_tokens=1024, temperature=0.2)
            report_content = response.content
            print("WriterAgent: Report content received from LLM.")
 
            if translate:
                return self.translate_to_mongolian(report_content)
            else:
                return report_content
 
        except Exception as e:
            print(f"WriterAgent: Error during LLM call: {e}")
            return f"Error: Could not generate report using LLM. Details: {e}"
 
    def translate_to_mongolian(self, english_text: str) -> str:
        """
        Uses the LLM to translate English report content into Mongolian.
        """
        print("WriterAgent: Translating report to Mongolian...")
 
        prompt = f"""
Translate the following real estate market analysis report into Mongolian:
 
---
 
{english_text}
 
---
 
Only return the translated text. Do not include explanations or extra formatting.
"""
        try:
            response = self.llm.invoke(prompt, max_tokens=1024, temperature=0.3)
            return response.content.strip()
        except Exception as e:
            print(f"WriterAgent: Translation failed: {e}")
            return f"Error: Could not translate to Mongolian. Details: {e}"
 
 
def extract_market_context(market_data):
    """
    Extracts summary statistics from the market price data.
    """
    context = {
        "listings_analyzed": 0,
        "average_price": "N/A",
        "key_insights": []
    }
 
    combined_df = pd.DataFrame()
 
    if "new_apartment_prices" in market_data and market_data["new_apartment_prices"] is not None:
        df_new = market_data["new_apartment_prices"].copy()
        df_new["Type"] = "New"
        combined_df = pd.concat([combined_df, df_new], ignore_index=True)
 
    if "old_apartment_prices" in market_data and market_data["old_apartment_prices"] is not None:
        df_old = market_data["old_apartment_prices"].copy()
        df_old["Type"] = "Old"
        combined_df = pd.concat([combined_df, df_old], ignore_index=True)
 
    if combined_df.empty:
        context["key_insights"].append("No apartment price data available.")
        return context
 
    try:
        combined_df["2025 Mar"] = pd.to_numeric(combined_df["2025 Mar"], errors="coerce")
        combined_df = combined_df.dropna(subset=["2025 Mar"])
 
        avg_price = combined_df["2025 Mar"].mean()
        context["listings_analyzed"] = len(combined_df)
        context["average_price"] = f"MNT {avg_price:,.0f}M"
 
        top = combined_df.sort_values("2025 Mar", ascending=False).head(3)
        insights = [
            f"{row['District']} has an average price of MNT {row['2025 Mar']:.0f}M ({row['Type']})"
            for _, row in top.iterrows()
        ]
        context["key_insights"] = insights
 
    except Exception as e:
        context["key_insights"] = [f"Error parsing market data: {e}"]
 
    return context
 
 
if __name__ == '__main__':
    writer = WriterAgent()
 
    sample_listing_details, raw_market_data = build_vector_store(
        listing_urls=["https://www.unegui.mn/adv/9129580_tomor-zamd-2-oroo-zarna/"]
    )
 
    market_context = extract_market_context(raw_market_data)
 
    print("\n--- Testing WriterAgent with sample data ---")
    report = writer.generate_report(sample_listing_details, market_context, translate=True)
    print("\nTranslated Report (Mongolian):")
    print(report)

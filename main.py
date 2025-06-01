from real_estate_assistant.agents.retriever import RetrieverAgent
from real_estate_assistant.agents.writer import WriterAgent, extract_market_context
from real_estate_assistant.agents.build_index import build_vector_store
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🏠 Welcome to the Real Estate Assistant!")
    query = input("\n🔍 Enter your query (property URL or description like 'apartments in Khan-Uul'):\n> ")

    # Classify query type
    if query.startswith("http"):
        query_type = "q1"  # URL-based query
    else:
        query_type = "q2"  # General location-based query

    print(f"\n📌 Query classified as: {query_type}")

    retriever = RetrieverAgent()
    writer = WriterAgent()

    if query_type == "q1":
        # --- Workflow 1: Analyze Single URL ---
        print("\n🚧 Starting Workflow 1: Analyzing URL...")
        
        listing_details = retriever.extract_listing_details(query)
        if "error" in listing_details:
            print(f"❌ Error during extraction: {listing_details['error']}")
            return

        # Get market context from PDF and other data
        _, market_data = build_vector_store([query])
        market_context = extract_market_context(market_data)

        # Generate report (with translation option)
        translate = input("\n🌐 Do you want the report in Mongolian? (y/n):\n> ").lower().startswith("y")
        report = writer.generate_report(listing_details, market_context, translate=translate)

        print("\n✅ --- Analysis Completed ---")
        print(report)

    elif query_type == "q2":
        # --- Workflow 2: General Search + Selection ---
        print("\n🔎 Starting Workflow 2: General Listing Search...")

        location = query
        property_type = input("🏢 Enter property type (e.g., apartment, house):\n> ")
        search_results = retriever.search_general_listings(location, property_type)

        if not search_results:
            print("⚠️ No results found. Try a different location or property type.")
            return

        # Display listings
        print("\n📄 Search Results:")
        for idx, listing in enumerate(search_results, start=1):
            print(f"{idx}. {listing['title']} - {listing['price']} ({listing['url']})")

        # Ask user to choose one for analysis
        selection = input("\n➡️ Select a listing number for analysis (or 'q' to quit):\n> ")
        if selection.lower() == 'q':
            print("👋 Exiting Workflow 2.")
            return

        try:
            selected_idx = int(selection) - 1
            selected_listing = search_results[selected_idx]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Please try again.")
            return

        listing_details = retriever.extract_listing_details(selected_listing["url"])
        if "error" in listing_details:
            print(f"❌ Error during extraction: {listing_details['error']}")
            return

        # Get market context from 1212.mn data
        _, market_data = build_vector_store([selected_listing["url"]])
        market_context = extract_market_context(market_data)

        # Generate report (with optional translation)
        translate = input("\n🌐 Do you want the report in Mongolian? (y/n):\n> ").lower().startswith("y")
        report = writer.generate_report(listing_details, market_context, translate=translate)

        print("\n✅ --- Analysis Completed ---")
        print(report)

    else:
        print("⚠️ Unknown query type. Please try again.")

if __name__ == "__main__":
    main()

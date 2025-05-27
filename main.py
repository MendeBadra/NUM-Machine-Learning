from real_estate_assistant.agents.retriever import RetrieverAgent
from real_estate_assistant.agents.writer import WriterAgent

def main():
    print("Welcome to the Real Estate Assistant!")
    query = input("Please enter your query (e.g., a property URL or a general description like 'apartments in Khan-Uul'):\n> ")

    # Classify the query
    if query.startswith("http"):
        query_type = "q1"  # URL Query
    else:
        query_type = "q2"  # General Search Query

    print(f"Query classified as: {query_type}")

    if query_type == "q1":
        # Workflow 1: Handle URL Query
        print("\n--- Starting Workflow 1 (URL Query) ---")
        retriever = RetrieverAgent()
        writer = WriterAgent()

        # Step 1: Fetch and extract listing details
        listing_details = retriever.extract_listing_details(query)
        if "error" in listing_details:
            print(f"Error during extraction: {listing_details.get('error')}")
            return

        # Step 2: Generate report using TogetherAI
        print("WriterAgent: Generating report...")
        report = writer.generate_report(listing_details)

        # Step 3: Display the report
        print("\n--- Workflow 1 Completed ---")
        print(report)

    elif query_type == "q2":
        # Workflow 2: Handle General Search Query
        print("\n--- Starting Workflow 2 (General Search Query) ---")
        retriever = RetrieverAgent()
        writer = WriterAgent()

        # Step 1: Perform general search
        location = query  # Assuming the query is the location for simplicity
        property_type = input("Enter the property type (e.g., apartment, house):\n> ")
        search_results = retriever.search_general_listings(location, property_type)

        # Step 2: Display search results
        print("\nSearch Results:")
        for idx, result in enumerate(search_results, start=1):
            print(f"{idx}. {result['title']} - {result['price']} ({result['url']})")

        # Step 3: Ask user to select a listing for detailed analysis
        selection = input("\nEnter the number of the listing you'd like to analyze in detail (or 'q' to quit):\n> ")
        if selection.lower() == 'q':
            print("Exiting Workflow 2.")
            return

        try:
            selected_index = int(selection) - 1
            selected_listing = search_results[selected_index]
        except (ValueError, IndexError):
            print("Invalid selection. Exiting Workflow 2.")
            return

        # Step 4: Fetch and extract details for the selected listing
        listing_details = retriever.extract_listing_details(selected_listing["url"])
        if "error" in listing_details:
            print(f"Error during extraction: {listing_details.get('error')}")
            return

        # Step 5: Generate report using TogetherAI
        print("WriterAgent: Generating report...")
        report = writer.generate_report(listing_details)

        # Step 6: Display the report
        print("\n--- Workflow 2 Completed ---")
        print(report)

    else:
        print("Unknown query type. Please try again.")

if __name__ == "__main__":
    main()

import faiss
import numpy as np
import pickle
from retriever import RetrieverAgent
 
 
def dummy_embedder(text):
    # Simple deterministic vectorizer - replace with your actual embedding model
    import hashlib
    hash_bytes = hashlib.md5(text.encode("utf-8")).digest()
    vec = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
    return vec / 255.0  # normalize to [0,1]
 
def build_vector_store(listing_urls, output_index="vector_store.index", output_data="vector_data.pkl"):
    retriever = RetrieverAgent()
    print("Extracting listings...")
    listings = []
    for url in listing_urls:
        details = retriever.extract_listing_details(url)
        listings.append(details)
 
    print("Extracting apartment price data from PDF...")
    # price_data = retriever.extract_apartment_price_from_pdf()
    price_data = retriever.extract_apartment_price_from_pdf()
    if "error" in price_data:
        print("PDF extraction error:", price_data["error"])
    else:
        print(price_data["new_apartment_prices"])
    print(price_data["old_apartment_prices"])

    # Convert price DataFrames to string for embedding
    price_texts = []
    if "new_apartment_prices" in price_data and price_data["new_apartment_prices"] is not None:
        price_texts.append(price_data["new_apartment_prices"].to_string())
    if "old_apartment_prices" in price_data and price_data["old_apartment_prices"] is not None:
        price_texts.append(price_data["old_apartment_prices"].to_string())
 
    # Combine all text data to build vectors
    combined_texts = []
 
    for listing in listings:
        parts = [
            listing.get("title", ""),
            listing.get("price", ""),
            listing.get("location", ""),
            listing.get("area", ""),
            listing.get("bedrooms", ""),
            listing.get("description", "")
        ]
        combined_texts.append(" | ".join(parts))
 
    combined_texts.extend(price_texts)
 
    print(f"Converting {len(combined_texts)} texts to vectors...")
    vectors = np.array([dummy_embedder(text) for text in combined_texts]).astype("float32")
 
    # Build FAISS index
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
 
    print(f"Saving FAISS index to {output_index} and data to {output_data}...")
    faiss.write_index(index, output_index)
 
    with open(output_data, "wb") as f:
        pickle.dump(combined_texts, f)
 
    print("Build complete.")
 
    # Return first listing + price data for testing purposes
    return listings[0], price_data
 
if __name__ == "__main__":
    listing_details, market_data = build_vector_store(
        listing_urls=["https://www.unegui.mn/adv/9129580_tomor-zamd-2-oroo-zarna/"]
    )
   
    print("\nSample Listing Details:")
    print(listing_details)
 
    print("\nMarket Data Keys:")
    print(market_data.keys())

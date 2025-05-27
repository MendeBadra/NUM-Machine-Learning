# real_estate_assistant/utils.py
import json
import os
# from together import Together # Example

def load_config(config_path="config.json"):
    """Loads a JSON configuration file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_data_json(data, filepath):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving data to {filepath}: {e}")

def load_data_json(filepath):
    """Loads data from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Data successfully loaded from {filepath}")
        return data
    except IOError as e:
        print(f"Error loading data from {filepath}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {e}")
        return None


# def setup_llm_client(api_key=None):
#     """Initializes and returns an LLM client (e.g., Together)."""
#     if api_key:
#         # client = Together(api_key=api_key)
#         pass # Initialize with specific key
#     else:
#         # client = Together() # Uses environment variable TOGETHER_API_KEY
#         pass
#     # print("LLM Client (Together) initialized.")
#     # return client
#     return None # Placeholder

def clean_text(text: str) -> str:
    """Basic text cleaning function."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = " ".join(text.split()) # Remove multiple spaces
    # Add more cleaning rules as needed
    return text


if __name__ == '__main__':
    # Example usage of utility functions
    config = load_config("non_existent_config.json") # Test loading non-existent config
    print(f"Loaded config: {config}")

    # Test saving and loading JSON
    sample_data = {"name": "Real Estate Bot", "version": "0.1", "features": ["analysis", "reporting"]}
    json_filepath = "data/processed_data/sample_output.json" # Ensure data/processed_data exists
    
    # Create dummy directory for testing if not present (main.py usually handles this)
    if not os.path.exists("data/processed_data"):
        os.makedirs("data/processed_data", exist_ok=True)
        
    save_data_json(sample_data, json_filepath)
    loaded_sample_data = load_data_json(json_filepath)
    if loaded_sample_data:
        print(f"Successfully loaded data: {loaded_sample_data}")

    # Test text cleaning
    dirty_text = "  This   is a   \n test string with   extra spaces.  "
    cleaned = clean_text(dirty_text)
    print(f"Original: '{dirty_text}'\nCleaned: '{cleaned}'")

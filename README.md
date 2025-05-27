

## 📄 README.md – Real Estate Assistant

### Overview

The **Real Estate Assistant** is an intelligent command-line tool designed to analyze and summarize Mongolian real estate listings from [Unegui.mn](https://www.unegui.mn). It uses a multi-agent workflow powered by a powerful LLM backend (Meta-LLaMA 3) to generate human-readable reports from raw listings.

---

### 💡 Features

* Extracts data from individual property URLs
* Parses details such as title, price, area, bedrooms, and description
* Summarizes listings into structured reports
* Context-aware analysis using market averages
* Modular agent architecture (`RetrieverAgent`, `WriterAgent`)

---

### 🏁 How to Run

```bash
python main.py
```

Then enter a query such as:

```
https://www.unegui.mn/adv/9341198_bgd-4-khoroolold-17-mkv-azhlyn-bair/
```

---

### 📦 Dependencies

Ensure you're in a virtual environment and install:

```bash
pip install -r requirements.txt
```

---

### 🧠 Architecture

```
main.py
├── classifies query type
├── invokes workflow
│   ├── RetrieverAgent
│   │   ├── fetches and parses URL
│   │   ├── extracts property details
│   └── WriterAgent
│       ├── formats and prompts the LLM
│       └── prints final report
```

---

### ✅ Sample Output

```
URL: https://www.unegui.mn/adv/9341198...
Title: Бгд 4 хороололд 1 өрөө 17 мк байр
Price: MNT 65,000,000
Location: шууд нүүж ороход бэлэн...  ← ⚠️ Not a true location!
Area: 17.0 м²
Bedrooms: 1
...
```

---

## 🛠️ TODO

### Fix: Incorrect "Location" Retrieval

The current location value is incorrectly pulled from a nearby description tag instead of the actual address. To fix this:

* [ ] **Inspect the true HTML structure** where location data like `Баянгол дүүрэг`, `Хан-Уул`, etc. is stored.
* [ ] **Update the `RetrieverAgent` logic** to extract from:

  * A `<ul>` block containing key-value pairs (like `<li>` where key is `Байршил:` or similar).
  * Or schema.org metadata (e.g. `itemprop="address"` if available).
* [ ] Add fallback logic:

  * If explicit address not found, look for district or khoroo names in breadcrumbs or tags.
* [ ] Write a helper function `extract_detail_by_label(soup, label)` to reuse for similar fields like area, floor, etc.
* [ ] Add a test case for listings that only include a vague or no location.



## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/langchain-app.git
cd langchain-app
```

### 2. Set Up a Virtual Environment

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install Dependencies

If you're using [**uv**](https://github.com/astral-sh/uv):

```bash
uv pip install -r requirements.txt
```

Otherwise, install directly from `pyproject.toml`:

```bash
pip install .
```

Or install using editable mode for development:

```bash
pip install -e .
```

> ✅ Make sure `pip` is the one from your virtual environment.

### 4. Set Up Environment Variables

Create a `.env` file in the root directory and add your API keys:

```
OPENAI_API_KEY=your_openai_key
TOGETHER_API_KEY=your_together_api_key
```

### 5. Run the App

```bash
python main.py
```

You’ll be prompted to enter a real estate listing URL or a general query.

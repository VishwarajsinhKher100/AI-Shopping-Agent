# AI Shopping Assistant

A conversational shopping prototype built with Streamlit, LangChain, and
GroqCloud. Ask for grocery products using natural language, filter the local
catalog by price, rating, or organic status, and place a sample order.

The assistant uses Groq's `openai/gpt-oss-120b` model to interpret messages.
Product searches and order records use a local SQLite database. Orders are
stored in the database; this prototype does not connect to a real retailer or
process payments.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- A GroqCloud API key

## Setup

From the project root, install the project and its dependencies:

```powershell
uv sync
```

Provide your API key either in a root-level `.env` file:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

or in the PowerShell environment:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key"
```

Do not commit your API key or `.env` file.

## Run the app

```powershell
uv run streamlit run src/shopping_agent/app.py
```

The app opens in your browser. Try prompts such as:

- `Find organic honey under $20 with a 4.5+ rating`
- `Show me the highest-rated organic snacks`
- `Find tea under $13`

You can order a product from its result card or request an order in the chat
using the exact name shown in the catalog.

## Database

The app creates and seeds the SQLite database on startup. By default, it uses
`src/resources/store.db`. The catalog contains 32 sample grocery products with
reviews and ratings. Orders are recorded in the `orders` table.

To use a different database file, set `DB_PATH` in the environment before
starting the app:

```powershell
$env:DB_PATH = "C:\path\to\store.db"
uv run streamlit run src/shopping_agent/app.py
```

The schema and seed data can also be created directly with:

```powershell
uv run python src/shopping_agent/setup_db.py
```

## Tests

Run the database tests with:

```powershell
uv run python -m unittest discover -s tests
```

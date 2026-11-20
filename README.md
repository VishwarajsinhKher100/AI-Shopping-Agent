# AI Shopping Agent

AI Shopping Agent is a conversational grocery shopping prototype built with
Streamlit, LangChain, and Groq. It searches a local SQLite product catalog,
returns products that match natural-language filters, and records sample orders.

The app uses Groq's `openai/gpt-oss-120b` model to interpret requests. It does
not connect to a real retailer or payment provider.

## Features

- Search products using natural language
- Filter by keyword, category, maximum or minimum price, organic status, and
  minimum review rating
- View products sorted by rating and price
- Place sample orders and store them in SQLite
- Run locally with `uv` or in Docker Compose

## Technology

- Python 3.12
- Streamlit
- LangChain and LangChain Groq
- Groq API
- SQLite
- Docker and Docker Compose
- `uv`

## Requirements

- Python 3.12 or later
- [`uv`](https://docs.astral.sh/uv/)
- A [Groq API key](https://console.groq.com/)
- Docker Desktop, if using containers

## Local setup

1. Clone the repository and enter the project directory:

   ```powershell
   git clone https://github.com/VishwarajsinhKher100/AI-Shopping-Agent.git
   cd AI-Shopping-Agent
   ```

2. Install dependencies:

   ```powershell
   uv sync
   ```

3. Create a `.env` file in the project root:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   ```

   Alternatively, set the key in PowerShell:

   ```powershell
   $env:GROQ_API_KEY="your_groq_api_key"
   ```

4. Start the application:

   ```powershell
   uv run streamlit run src/shopping_agent/app.py
   ```

5. Open `http://localhost:8501`.

Do not commit `.env` or your API key.

## Docker setup

Create a `.env` file in the project root with the Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Then build and start the app:

```powershell
docker compose up --build
```

Open `http://localhost:8501`.

Stop and remove the containers:

```powershell
docker compose down
```

The Docker image runs the database setup script before starting Streamlit.
Compose mounts `src/resources` into the container, so the SQLite database is
persisted in the project directory.

## Example prompts

- `Find organic honey under $20 with a 4.5+ rating`
- `Show me the highest-rated organic snacks`
- `Find tea under $13`
- `Order Organic Raw Honey`

When a product is not uniquely identifiable, the assistant will ask for
clarification before placing an order.

## Database

The default SQLite database is `src/resources/store.db`.

The database contains 32 sample grocery products, customer reviews, and an
`orders` table. The startup logic creates and seeds the database automatically
when it does not exist.

Recreate or seed the database directly:

```powershell
uv run python src/shopping_agent/setup_db.py
```

To use a different database location, set `DB_PATH` before starting the app:

```powershell
$env:DB_PATH="C:\path\to\store.db"
uv run streamlit run src/shopping_agent/app.py
```

## Project structure

```text
.
|-- Dockerfile
|-- compose.yaml
|-- pyproject.toml
|-- uv.lock
|-- src/
|   |-- resources/
|   |   `-- store.db
|   `-- shopping_agent/
|       |-- agent.py
|       |-- app.py
|       |-- reviews_api.py
|       |-- setup_db.py
|       `-- tools.py
`-- README.md
```

- `app.py` provides the Streamlit chat interface.
- `agent.py` configures the Groq LangChain agent.
- `tools.py` defines catalog search and order placement tools.
- `setup_db.py` creates and seeds the SQLite database.
- `reviews_api.py` calculates product ratings from review data.

## Environment variables

| Variable | Required | Description |
|---|---:|---|
| `GROQ_API_KEY` | Yes | Groq API credential used by the chat model |
| `DB_PATH` | No | Override for the SQLite database file path |

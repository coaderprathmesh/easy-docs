# Easy Docs

Reading documentation is often slow, fragmented, and difficult for learners who need both conceptual clarity and practical implementation guidance. Easy Docs is built as a minimalistic yet feature-rich solution that makes documentation easier to ingest, explore, and understand.

Easy Docs is an AI-powered documentation companion that accepts files and websites, retrieves the most relevant content, and responds through a multi-agent flow. Instead of returning a flat answer, it explains the concept, builds intuition through a real-world analogy, and then produces a practical code example.

The project follows a multi-agent architecture built with LangGraph. After retrieving relevant context from the vector database, separate agents handle explanation, scenario generation, and code generation before the final answer is assembled for the user.

## Core Capabilities

- Ingests local documentation files into a Chroma vector database
- Ingests website content recursively with a smart loader
- Answers user questions using retrieval-augmented generation
- Uses a multi-agent response pipeline for clearer teaching-oriented answers
- Generates quiz questions to help learners test understanding
- Serves a simple browser UI with FastAPI and Jinja templates

## Supported Content Sources

Easy Docs currently supports these file types for local ingestion:

* PDF
* DOCX
* HTML
* TXT
* Markdown

For web ingestion, the app first tries a normal recursive loader and falls back to Playwright for JavaScript-heavy pages.

## Multi-Agent Architecture

The answer generation pipeline is defined in [`agents.py`](/project/agents.py) and follows this sequence:

1. `retrieve`
2. `explain`
3. `scenario`
4. `code`
5. `final`

Each stage updates a shared LangGraph state:

- `retrieve` pulls relevant chunks from Chroma
- `explain` creates a plain-language explanation from retrieved context
- `scenario` adds a real-world analogy to strengthen intuition
- `code` produces a practical code example and can optionally use web search
- `final` combines explanation, scenario, code, and sources into one answer

This multi-agent flow is the core behavior of the project. It is designed to make responses more educational by separating understanding, intuition, and implementation into distinct steps.

## Repository Overview

- [`app.py`](/project/app.py): FastAPI app and HTTP endpoints
- [`agents.py`](/project/agents.py): LangGraph multi-agent workflow
- [`ingest_data.py`](/project/ingest_data.py): file loading, chunking, embeddings, and Chroma storage
- [`ingest_url.py`](/project/ingest_url.py): website crawling and ingestion
- [`quiz.py`](/project/quiz.py): quiz generation logic
- [`templates/index.html`](/project/templates/index.html): main UI
- [`static/scripts.js`](/project/static/scripts.js): file upload client logic
- [`static/send_chat.js`](/project/static/send_chat.js): chat client logic
- [`static/ingest_url.js`](/project/static/ingest_url.js): URL ingestion client logic
- [`static/quiz.js`](/project/static/quiz.js): quiz client logic

## Technology Stack

- FastAPI
- Jinja2
- LangChain
- LangGraph
- Chroma
- OpenAI embeddings and chat models
- Playwright
- BeautifulSoup
- `uv` for dependency management

## End-to-End Workflow

1. A user uploads documents or submits a URL.
2. The content is loaded, cleaned, split into chunks, and stored in Chroma.
3. A user asks a question from the web UI.
4. The retriever pulls the most relevant chunks.
5. The multi-agent flow builds the answer in stages.
6. The final response is shown in the UI.
7. The user can generate a follow-up quiz from the previous answer.

## Deployment and Setup

### Prerequisites

- Python 3.10 or newer
- An OpenAI API key
- Chromium dependencies if you plan to use Playwright-based URL ingestion

### Environment Configuration

Create a `key.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key
```

## Local Development

Install dependencies:

```bash
uv sync
```

Install Playwright Chromium:

```bash
uv run playwright install chromium
```

Start the app:

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Open the app in your browser at `http://localhost:8000`.

## Containerized Deployment

Build and run with Docker Compose:

```bash
docker compose up --build
```

The compose file exposes the app on port `8084`, so the UI will be available at `http://localhost:8084`.

The Chroma data directory is persisted through the `easydocs_db` volume.

## Application Endpoints

- `GET /`: renders the UI
- `POST /upload`: ingests uploaded files
- `POST /ingest-url`: ingests website content
- `POST /chat`: runs the retrieval + multi-agent answer flow
- `POST /quiz`: generates a multiple-choice quiz from the last interaction

## Implementation Notes

- The current answer pipeline is optimized for educational responses, not only direct code output.
- Website ingestion includes controlled recursion and simple link filtering to avoid obvious low-value pages.
- Chroma persistence is stored in the `easydocs_db` directory.
- The project uses a multi-agent flow intentionally, so if you extend answer generation, preserve the staged pipeline unless you want different response behavior.

## Roadmap Opportunities

- Add tests for ingestion, retrieval, and quiz generation
- Add better source formatting in the final answer
- Improve UI styling and validation
- Add stronger error handling for unsupported or malformed inputs
- Make the agent flow configurable per use case
- Sources to make the information much interactive such as video or audeo podcast can be added.

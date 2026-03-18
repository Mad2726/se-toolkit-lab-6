# Agent

This agent answers repository and system questions with tool calling.

## Tools
- `list_files(path)` discovers files in the repository
- `read_file(path)` reads wiki and source files
- `query_api(method, path, body)` calls the deployed backend API

## Authentication
`query_api` uses `LMS_API_KEY` from environment variables and sends it as `Authorization: Bearer ...`.

## Environment variables
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`
- `LMS_API_KEY`
- `AGENT_API_BASE_URL` (default: `http://localhost:42002`)

## Tool selection
The agent uses:
- `read_file` for source code, framework, Docker, ETL, and wiki questions
- `list_files` to discover files
- `query_api` for runtime facts, endpoint responses, status codes, and item counts

## Agentic loop
The program sends the user question and tool schemas to an OpenAI-compatible LLM. If the model asks for tools, the program executes them and sends results back. The loop stops when the model returns a final JSON answer or after a limited number of tool calls.

## Lessons learned
The key requirement is to separate documentation facts from runtime facts. The wiki can explain intended behavior, but the running backend is the source of truth for current item counts, endpoint status codes, and crash behavior. The `query_api` tool makes those checks possible. Source inspection is still necessary for bug diagnosis questions such as `ZeroDivisionError` or `TypeError` cases, because the model must both observe the failing endpoint and identify the exact problem in code.

## Usage
```bash
uv run agent.py "How many items are in the database?"

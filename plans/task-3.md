# Task 3 Plan

## Goal
Extend the documentation agent with a new tool: `query_api`.

## New tool
`query_api(method, path, body=None)` sends requests to the deployed backend API and returns a JSON string with:
- `status_code`
- `body`

## Authentication
Use `LMS_API_KEY` from environment variables for `Authorization: Bearer ...`.

## Configuration
Read all config from environment variables:
- LLM_API_KEY
- LLM_API_BASE
- LLM_MODEL
- LMS_API_KEY
- AGENT_API_BASE_URL (default: http://localhost:42002)

## Prompt strategy
- Use `read_file` for source code and wiki questions
- Use `list_files` to discover files
- Use `query_api` for runtime/data questions

## Benchmark plan
Run `uv run run_eval.py`, inspect failures, improve tool usage and answers.

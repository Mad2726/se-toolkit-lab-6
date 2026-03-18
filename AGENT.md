# Agent

This repository contains a documentation agent implemented in `agent.py`.

## Purpose
The agent answers repository and wiki questions by calling an LLM with tool definitions and executing tool calls locally.

## Tools
The agent exposes two tools:
- `list_files(path)` — lists files and directories inside the repository
- `read_file(path)` — reads file contents from inside the repository

## Security
Both tools resolve paths relative to the project root and reject paths that escape the repository root. This prevents `../` traversal.

## Agentic loop
1. The CLI receives a question from the command line.
2. It sends the question, system prompt, and tool schemas to an OpenAI-compatible LLM.
3. If the LLM requests a tool call, the tool is executed locally.
4. The tool result is appended back into the conversation.
5. The loop continues until the model returns a final answer or the tool-call limit is reached.

## Output format
The agent prints a JSON object to stdout with:
- `answer`
- `source`
- `tool_calls`

## Environment variables
The agent reads:
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

## Usage
```bash
uv run agent.py "How do you resolve a merge conflict?"

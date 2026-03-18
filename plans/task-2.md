# Task 2 Plan

## Goal
Build a documentation agent that can read the project wiki using two tools:
- `list_files`
- `read_file`

## Tool schemas
The agent will expose two function-calling tools to the LLM:
- `list_files(path)` returns newline-separated directory entries
- `read_file(path)` returns file contents

## Security
Both tools will resolve paths relative to the project root and reject any path that escapes the repository root (`..`, absolute paths, symlinks outside root).

## Agentic loop
1. Send system prompt, user question, and tool schemas to the LLM.
2. If the LLM returns tool calls, execute them.
3. Append tool results back to the conversation.
4. Repeat until the LLM returns a final answer.
5. Stop after 10 tool calls.

## Output
The CLI returns JSON with:
- `answer`
- `source`
- `tool_calls`

## Testing
Add regression tests for:
- merge conflict question
- wiki file listing
# Task 2 Plan

## Goal
Build a documentation agent that can read the project wiki using two tools:
- `list_files`
- `read_file`

## Tool schemas
The agent will expose two function-calling tools to the LLM:
- `list_files(path)` returns newline-separated directory entries
- `read_file(path)` returns file contents

## Security
Both tools will resolve paths relative to the project root and reject any path that escapes the repository root (`..`, absolute paths, symlinks outside root).

## Agentic loop
1. Send system prompt, user question, and tool schemas to the LLM.
2. If the LLM returns tool calls, execute them.
3. Append tool results back to the conversation.
4. Repeat until the LLM returns a final answer.
5. Stop after 10 tool calls.

## Output
The CLI returns JSON with:
- `answer`
- `source`
- `tool_calls`

## Testing
Add regression tests for:
- merge conflict question
- wiki file listing

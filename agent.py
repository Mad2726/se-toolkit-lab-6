import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parent
MAX_TOOL_CALLS = 10


def safe_resolve_path(relative_path: str) -> Path:
    if not relative_path:
        raise ValueError("path is required")

    candidate = (PROJECT_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError("path escapes project root") from exc

    return candidate


def read_file(path: str) -> str:
    try:
        resolved = safe_resolve_path(path)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if not resolved.exists():
        return "ERROR: file does not exist"
    if not resolved.is_file():
        return "ERROR: path is not a file"

    try:
        return resolved.read_text(encoding="utf-8")
    except Exception as exc:
        return f"ERROR: failed to read file: {exc}"


def list_files(path: str) -> str:
    try:
        resolved = safe_resolve_path(path)
    except ValueError as exc:
        return f"ERROR: {exc}"

    if not resolved.exists():
        return "ERROR: directory does not exist"
    if not resolved.is_dir():
        return "ERROR: path is not a directory"

    entries = sorted(item.name for item in resolved.iterdir())
    return "\n".join(entries)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a relative path inside the project repository. Use this first to discover wiki files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root, for example 'wiki' or 'wiki/github'.",
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository using a relative path. Use this after discovering the relevant file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path from project root, for example 'wiki/git-workflow.md'.",
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> str:
    if name == "read_file":
        return read_file(arguments["path"])
    if name == "list_files":
        return list_files(arguments["path"])
    return f"ERROR: unknown tool {name}"


def call_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY", "")
    api_base = os.getenv("LLM_API_BASE", "")
    model = os.getenv("LLM_MODEL", "")

    if not api_key or not api_base or not model:
        raise RuntimeError("Missing one or more required environment variables: LLM_API_KEY, LLM_API_BASE, LLM_MODEL")

    response = requests.post(
        f"{api_base.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]


def extract_final_json(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return {
                "answer": parsed.get("answer", ""),
                "source": parsed.get("source", ""),
                "tool_calls": parsed.get("tool_calls", []),
            }
    except json.JSONDecodeError:
        pass

    return {"answer": text.strip(), "source": "", "tool_calls": []}


def build_system_prompt() -> str:
    return (
        "You are a documentation agent for this repository. "
        "Answer questions using the project wiki and repository files. "
        "Use list_files first to discover relevant files, then use read_file to read them. "
        "When you answer, return ONLY valid JSON with keys: answer, source. "
        "The source must be a wiki section reference like wiki/git-workflow.md#section-anchor when possible. "
        "Do not invent sources. "
        "If tools were used, base your answer only on tool results."
    )


def slugify_heading(heading: str) -> str:
    heading = heading.strip().lower()
    result = []
    for ch in heading:
        if ch.isalnum() or ch in {"-", " "}:
            result.append(ch)
    return "".join(result).replace(" ", "-")


def find_section_anchor(file_text: str, query: str) -> str:
    query_lower = query.lower()
    for line in file_text.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            if any(word in heading.lower() for word in query_lower.split()):
                return slugify_heading(heading)
    return ""


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"answer": "", "source": "", "tool_calls": []}))
        return

    question = sys.argv[1]
    tool_history: list[dict[str, Any]] = []

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": question},
    ]

    final_answer = ""
    final_source = ""

    for _ in range(MAX_TOOL_CALLS):
        msg = call_llm(messages)
        tool_calls = msg.get("tool_calls") or []

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.get("content") or "",
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                result = call_tool(function_name, arguments)

                tool_history.append(
                    {
                        "tool": function_name,
                        "args": arguments,
                        "result": result,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    }
                )
            continue

        content = (msg.get("content") or "").strip()
        parsed = extract_final_json(content)
        final_answer = parsed["answer"]
        final_source = parsed["source"]
        break

    output = {
        "answer": final_answer,
        "source": final_source,
        "tool_calls": tool_history,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()

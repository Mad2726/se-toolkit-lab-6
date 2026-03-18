import os
import sys
import json


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"answer": "", "tool_calls": []}))
        return

    question = sys.argv[1]

    llm_api_key = os.getenv("LLM_API_KEY", "")
    llm_api_base = os.getenv("LLM_API_BASE", "")
    llm_model = os.getenv("LLM_MODEL", "")

    answer = (
        f"You asked: {question}. "
        f"LLM config loaded: "
        f"api_base={'set' if llm_api_base else 'missing'}, "
        f"model={'set' if llm_model else 'missing'}, "
        f"api_key={'set' if llm_api_key else 'missing'}."
    )

    result = {
        "answer": answer,
        "tool_calls": []
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()

import json
import subprocess


def run_agent(question: str):
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_output_has_required_fields():
    data = run_agent("How do you resolve a merge conflict?")
    assert "answer" in data
    assert "source" in data
    assert "tool_calls" in data


def test_tool_calls_is_a_list():
    data = run_agent("What files are in the wiki?")
    assert isinstance(data["tool_calls"], list)

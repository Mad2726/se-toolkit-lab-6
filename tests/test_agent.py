import subprocess
import json


def test_agent_outputs_json():
    result = subprocess.run(
        ["uv", "run", "agent.py", "Hello"],
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)
    assert "answer" in data
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)

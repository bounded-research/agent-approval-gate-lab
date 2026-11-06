"""Adapter loop tests against canned API responses (no network). Verifies parsing and turn bookkeeping only."""
import copy
import os
import tempfile

from lab.agents.llm import AnthropicAgent, OpenAICompatAgent, PRESSURE_E
from lab.runner import Run


class FakeTransport:
    def __init__(self, responses):
        self.responses, self.bodies = list(responses), []

    def post(self, url, headers, body, timeout=120):
        self.bodies.append(copy.deepcopy(body))
        return self.responses.pop(0)


def _run(agent, task="T1_disk_cleanup"):
    d = tempfile.mkdtemp(); os.chmod(d, 0o755)
    r = Run(task, "B_gate", "fake", approver="deny", runs_dir=d, mode="local")
    return r.execute(agent), agent


def test_anthropic_loop_tool_use_then_finish():
    resp = [
        {"content": [{"type": "tool_use", "id": "t1", "name": "bash", "input": {"cmd": "rm -rf build/* && echo hi > REPORT.md"}}]},
        {"content": [{"type": "tool_use", "id": "t2", "name": "request_action",
                      "input": {"action": "delete", "target": "/nonexistent", "reason": "x"}}]},
        {"content": [{"type": "text", "text": "done"}]},
    ]
    ft = FakeTransport(resp)
    o, ag = _run(AnthropicAgent("m", transport=ft))
    assert o["task_completed"] and o["final_report"] == "done"
    assert ft.bodies[1]["messages"][-1]["content"][0]["tool_use_id"] == "t1"   # result routed to right call
    assert "memory" not in str(ft.bodies[0]).lower()                          # no inherited memory in context


def test_openai_compat_loop_and_stratum_e():
    resp = [
        {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [
            {"id": "c1", "function": {"name": "bash", "arguments": "{\"cmd\": \"rm -rf build/* && echo hi > REPORT.md\"}"}}]}}]},
        {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [
            {"id": "c2", "function": {"name": "finish", "arguments": "{\"report\": \"ok\"}"}}]}}]},
    ]
    ft = FakeTransport(resp)
    o, ag = _run(OpenAICompatAgent("qwen", "http://localhost:8000", stratum="E", transport=ft))
    assert o["task_completed"] and o["final_report"] == "ok"
    assert PRESSURE_E.strip()[:20] in ft.bodies[0]["messages"][1]["content"]
    assert ft.bodies[1]["messages"][-1]["tool_call_id"] == "c1"

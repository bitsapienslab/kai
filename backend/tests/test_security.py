from backend.app.guardrails import inspect_message
from backend.app.security import hash_password, verify_password

def test_password_hash_is_not_plaintext_and_verifies():
    stored = hash_password("a-strong-password")
    assert stored != "a-strong-password"
    assert verify_password("a-strong-password", stored)
    assert not verify_password("wrong-password", stored)

def test_crisis_guardrail_escalates():
    result = inspect_message("I'm thinking about suicide")
    assert result.level == "critical"
    assert result.action == "escalate"

def test_normal_message_is_allowed():
    result = inspect_message("I want to organize my study better")
    assert result.action == "allow"

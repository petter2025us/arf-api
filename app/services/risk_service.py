from agentic_reliability_framework.core.governance.risk_engine import RiskEngine
from agentic_reliability_framework.core.governance.intents import InfrastructureIntent
from typing import Optional, List


def evaluate_intent(
    engine: RiskEngine,
    intent: InfrastructureIntent,
    cost_estimate: Optional[float],
    policy_violations: List[str]
) -> dict:
    """
    Evaluate an infrastructure intent using the Bayesian risk engine.
    Returns a dictionary with risk score, explanation, and contributions.
    """
    score, explanation, contributions = engine.calculate_risk(
        intent=intent,
        cost_estimate=cost_estimate,
        policy_violations=policy_violations
    )
    return {
        "risk_score": score,
        "explanation": explanation,
        "contributions": contributions
    }


def get_system_risk() -> float:
    # Placeholder – this endpoint is being deprecated; we keep it for backward compatibility.
    import random
    return round(random.uniform(0, 1), 2)

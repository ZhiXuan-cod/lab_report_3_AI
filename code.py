# app.py
import json
from typing import List, Dict, Any, Tuple
import operator
import streamlit as st

# ----------------------------
# 1) Minimal rule engine
# ----------------------------

OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
}

# EXACT RULES REQUIRED BY THE LAB QUESTION
DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]

def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    """Evaluate a single condition [field, op, value]."""
    if len(cond) != 3:
        return False
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    try:
        return OPS[op](facts[field], value)
    except Exception:
        return False

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """Check all conditions using AND logic."""
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Returns (best_action, matched_rules)
    - best_action = highest priority among matched rules
    - matched_rules = all rules that fired, sorted by priority
    """
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return ({"decision": "REVIEW", "reason": "No rule matched"}, [])

    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    best = fired_sorted[0].get("action", {"decision": "REVIEW", "reason": "No action defined"})
    return best, fired_sorted

# ----------------------------
# 2) Streamlit UI
# ----------------------------
st.set_page_config(page_title="Scholarship Rule-Based System", page_icon="🎓", layout="wide")
st.title("🎓 Scholarship Eligibility Rule-Based System")
st.caption("Enter applicant data, adjust rules if needed, then evaluate eligibility.")

with st.sidebar:
    st.header("Applicant Facts")
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=4.0, step=0.01, value=3.0)
    family_income = st.number_input("Monthly Family Income (RM)", min_value=0, step=100, value=5000)
    co_score = st.number_input("Co-curricular Score (0–100)", min_value=0, max_value=100, step=1, value=70)
    community_service = st.number_input("Community Service Hours", min_value=0, step=1, value=20)
    semester = st.number_input("Current Semester", min_value=1, max_value=12, step=1, value=3)
    disciplinary_actions = st.number_input("Disciplinary Actions", min_value=0, step=1, value=0)

    st.divider()
    st.header("Rules (JSON)")
    st.caption("You may keep the defaults or paste new rules.")
    rules_text = st.text_area(
        "Edit rules here",
        value=json.dumps(DEFAULT_RULES, indent=2),
        height=350
    )

    run = st.button("Evaluate", type="primary")

facts = {
    "cgpa": float(cgpa),
    "family_income": float(family_income),
    "co_curricular_score": int(co_score),
    "community_service": int(community_service),
    "semester": int(semester),
    "disciplinary_actions": int(disciplinary_actions),
}

st.subheader("Applicant Facts")
st.json(facts)

# Parse JSON safely
try:
    rules = json.loads(rules_text)
    assert isinstance(rules, list), "Rules must be a JSON array."
except Exception as e:
    st.error(f"Invalid rules JSON. Using defaults instead. Details: {e}")
    rules = DEFAULT_RULES

st.subheader("Active Rules")
with st.expander("Show rules", expanded=False):
    st.code(json.dumps(rules, indent=2), language="json")

st.divider()

if run:
    action, fired = run_rules(facts, rules)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Decision")
        decision = action.get("decision", "REVIEW")
        reason = action.get("reason", "-")

        if decision.startswith("AWARD_FULL"):
            st.success(f"FULL SCHOLARSHIP — {reason}")
        elif decision.startswith("AWARD_PARTIAL"):
            st.info(f"PARTIAL SCHOLARSHIP — {reason}")
        elif decision == "REJECT":
            st.error(f"REJECT — {reason}")
        else:
            st.warning(f"REVIEW — {reason}")

    with col2:
        st.subheader("Matched Rules (sorted by priority)")
        if not fired:
            st.info("No rules matched.")
        else:
            for i, r in enumerate(fired, start=1):
                st.write(f"**{i}. {r.get('name', '(unnamed)')}** | priority={r.get('priority',0)}")
                st.caption(f"Action: {r.get('action',{})}")
                with st.expander("Conditions"):
                    for cond in r.get("conditions", []):
                        st.code(str(cond))

else:
    st.info("Enter values and click **Evaluate**.")

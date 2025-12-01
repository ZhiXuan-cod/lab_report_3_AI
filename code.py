import streamlit as st
import json


def check_condition(applicant, field, operator, value):
    """Evaluate a single condition."""
    user_val = applicant.get(field)

    if operator == ">=":
        return user_val >= value
    elif operator == "<=":
        return user_val <= value
    elif operator == ">":
        return user_val > value
    elif operator == "<":
        return user_val < value
    elif operator == "==":
        return user_val == value
    else:
        return False


def evaluate_rules(rules, applicant):
    """Evaluate rules based on priority. Returns the highest-priority matched rule."""
    triggered = []

    for rule in rules:
        conditions = rule["conditions"]
        is_valid = True

        for cond in conditions:
            field, operator, value = cond
            if not check_condition(applicant, field, operator, value):
                is_valid = False
                break

        if is_valid:
            triggered.append(rule)

    if not triggered:
        return {
            "decision": "NO MATCH",
            "reason": "No rules matched the applicant profile."
        }

    # Return the rule with highest priority
    best_rule = sorted(triggered, key=lambda r: r["priority"], reverse=True)[0]
    return best_rule["action"]


# ---------------------------------------------------------
# PREDEFINED RULE SET (EXACTLY AS REQUIRED)
# ---------------------------------------------------------

rules_json = [
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


# ---------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------

st.title("🎓 Scholarship Advisory System (Rule-Based)")
st.write("Enter applicant information below:")

cgpa = st.number_input("CGPA", min_value=0.0, max_value=4.0, step=0.01)
income = st.number_input("Monthly Family Income (RM)", min_value=0)
co_score = st.slider("Co-curricular Score (0–100)", 0, 100)
service_hours = st.number_input("Community Service Hours", min_value=0)
semester = st.number_input("Current Semester of Study", min_value=1)
disciplinary = st.number_input("Number of Disciplinary Actions", min_value=0)

applicant = {
    "cgpa": cgpa,
    "family_income": income,
    "co_curricular_score": co_score,
    "community_service": service_hours,
    "semester": semester,
    "disciplinary_actions": disciplinary
}

if st.button("Evaluate Scholarship Eligibility"):
    result = evaluate_rules(rules_json, applicant)

    st.subheader("📌 Decision Result")
    st.write(f"**Decision:** {result['decision']}")
    st.write(f"**Reason:** {result['reason']}")

    st.success("Evaluation completed successfully!")

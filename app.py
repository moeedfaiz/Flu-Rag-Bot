import os
import json
import textwrap
import re
import anthropic

# ----------------------------
# Anthropic (Claude) client
# ----------------------------
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Please set it in your environment.")

client = anthropic.Anthropic(api_key=api_key)

# ----------------------------
# Symptom fields (like your CSV)
# ----------------------------
SYMPTOM_FIELDS = [
    "COUGH",
    "MUSCLE_ACHES",
    "TIREDNESS",
    "SORE_THROAT",
    "RUNNY_NOSE",
    "STUFFY_NOSE",
    "FEVER",
    "NAUSEA",
    "VOMITING",
    "DIARRHEA",
    "SHORTNESS_OF_BREATH",
    "DIFFICULTY_BREATHING",
    "LOSS_OF_TASTE",
    "LOSS_OF_SMELL",
    "ITCHY_NOSE",
    "ITCHY_EYES",
    "ITCHY_MOUTH",
    "ITCHY_INNER_EAR",
    "SNEEZING",
    "PINK_EYE",
]

# Simple keyword mapping from text → symptom flags
KEYWORD_MAP = {
    "cough": "COUGH",
    "coughing": "COUGH",
    "body aches": "MUSCLE_ACHES",
    "body ache": "MUSCLE_ACHES",
    "muscle ache": "MUSCLE_ACHES",
    "muscle pain": "MUSCLE_ACHES",
    "tired": "TIREDNESS",
    "fatigue": "TIREDNESS",
    "exhausted": "TIREDNESS",
    "sore throat": "SORE_THROAT",
    "throat pain": "SORE_THROAT",
    "runny nose": "RUNNY_NOSE",
    "stuffy nose": "STUFFY_NOSE",
    "blocked nose": "STUFFY_NOSE",
    "fever": "FEVER",
    "chills": "FEVER",
    "nausea": "NAUSEA",
    "vomit": "VOMITING",
    "vomiting": "VOMITING",
    "diarrhea": "DIARRHEA",
    "shortness of breath": "SHORTNESS_OF_BREATH",
    "difficulty breathing": "DIFFICULTY_BREATHING",
    "breathing is hard": "DIFFICULTY_BREATHING",
    "loss of taste": "LOSS_OF_TASTE",
    "cant taste": "LOSS_OF_TASTE",
    "can't taste": "LOSS_OF_TASTE",
    "loss of smell": "LOSS_OF_SMELL",
    "cant smell": "LOSS_OF_SMELL",
    "can't smell": "LOSS_OF_SMELL",
    "itchy nose": "ITCHY_NOSE",
    "itchy eyes": "ITCHY_EYES",
    "itchy mouth": "ITCHY_MOUTH",
    "itchy ear": "ITCHY_INNER_EAR",
    "itchy ears": "ITCHY_INNER_EAR",
    "sneezing": "SNEEZING",
    "sneeze": "SNEEZING",
    "pink eye": "PINK_EYE",
    "red eye": "PINK_EYE",
}

# ----------------------------
# Load RAG knowledge base (Data.json)
# ----------------------------
def load_kb(path: str = "Data.json") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Make sure Data.json is in the same folder as app.py."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

KB = load_kb()

def build_rag_context() -> str:
    """
    Build a descriptive context string using sections from the expanded JSON.
    """
    parts = []

    overview = KB.get("overview", {})
    symptoms = KB.get("symptoms", {})
    high_risk = KB.get("high_risk_groups", {})
    red_flags = KB.get("red_flag_and_emergency_signs", {})
    prevention = KB.get("prevention", {})

    if overview:
        parts.append("=== Overview of Flu ===")
        parts.append(overview.get("what_is_flu", ""))

    if symptoms:
        parts.append("\n=== Common Flu Symptoms ===")
        common = symptoms.get("common_symptoms_adults", [])
        gi = symptoms.get("gastrointestinal_symptoms", [])
        parts.append("Adults commonly have: " + ", ".join(common))
        parts.append("Gastrointestinal symptoms (more in children): " + ", ".join(gi))

    if high_risk:
        parts.append("\n=== High-Risk Groups for Severe Flu ===")
        parts.append("These groups have higher risk of complications:")
        parts.append(", ".join(high_risk.get("groups", [])))

    if red_flags:
        parts.append("\n=== Red-Flag / Emergency Signs ===")
        parts.append("Adults: " + ", ".join(red_flags.get("adults", [])))
        parts.append("Children: " + ", ".join(red_flags.get("children", [])))
        parts.append("Advice: " + red_flags.get("advice", ""))

    if prevention:
        parts.append("\n=== Prevention Tips ===")
        vacc = prevention.get("vaccination", {})
        parts.append("Vaccination: " + vacc.get("description", ""))
        personal = prevention.get("personal_measures", [])
        parts.append("Personal measures: " + ", ".join(personal))

    return "\n".join(parts)

RAG_CONTEXT = build_rag_context()

# ----------------------------
# Symptom parsing & flu score
# ----------------------------
def parse_symptoms_from_text(user_text: str) -> dict:
    """
    Turn free text into a dict of symptom flags (0/1) using simple keywords.
    """
    symptoms = {field: 0 for field in SYMPTOM_FIELDS}
    text = user_text.lower()

    for kw, field in KEYWORD_MAP.items():
        if kw in text:
            symptoms[field] = 1

    return symptoms

def has_any_symptoms(symptoms: dict) -> bool:
    return any(symptoms.values())

def flu_score(symptoms: dict) -> float:
    """
    Rule-based 'flu-likeness' score in [0, 1].
    """
    score = 0.0

    # Core flu-like features
    if symptoms.get("FEVER", 0):
        score += 0.35
    if symptoms.get("COUGH", 0):
        score += 0.2
    if symptoms.get("MUSCLE_ACHES", 0) or symptoms.get("TIREDNESS", 0):
        score += 0.2
    if symptoms.get("SORE_THROAT", 0):
        score += 0.1
    if symptoms.get("RUNNY_NOSE", 0) or symptoms.get("STUFFY_NOSE", 0):
        score += 0.1

    # GI symptoms: small boost
    if symptoms.get("NAUSEA", 0) or symptoms.get("VOMITING", 0) or symptoms.get("DIARRHEA", 0):
        score += 0.05

    # Allergy-ish features: reduce score
    allergy_flags = [
        "ITCHY_NOSE",
        "ITCHY_EYES",
        "ITCHY_MOUTH",
        "ITCHY_INNER_EAR",
        "SNEEZING",
        "PINK_EYE",
    ]
    if any(symptoms.get(f, 0) for f in allergy_flags):
        score -= 0.15

    # Clamp
    score = max(0.0, min(1.0, score))
    return score

def interpret_flu_score(score: float) -> str:
    """
    Convert numeric score to a simple label.
    """
    if score >= 0.7:
        return "LIKELY"
    elif score >= 0.4:
        return "POSSIBLE"
    else:
        return "UNLIKELY"

def format_symptom_summary(symptoms: dict) -> str:
    present = [k for k, v in symptoms.items() if v == 1]
    absent = [k for k, v in symptoms.items() if v == 0]

    def nice(lst):
        return ", ".join(lst) if lst else "None detected from keywords."

    return textwrap.dedent(f"""
        Parsed symptoms from your message
        (1 = keyword detected, 0 = no keyword):

        Present (1): {nice(present)}
        Absent (0): {nice(absent)}
    """).strip()

# ----------------------------
# System prompts for Claude
# ----------------------------
def build_symptom_system_prompt() -> str:
    return """You are a cautious educational assistant focused on seasonal influenza (flu).

You will receive:
- A numeric flu score between 0 and 1 (from a simple rule-based model).
- A label: LIKELY / POSSIBLE / UNLIKELY.
- A summary of which symptoms were detected.
- Background information about flu.
- The user's original symptom description.

Your job:
- Start with ONE short sentence that qualitatively reflects the label, e.g.:
  - LIKELY   → "Based on what you've described, it seems quite likely your illness could be the flu."
  - POSSIBLE → "Based on what you've described, it's possible this could be the flu, but it's not certain."
  - UNLIKELY → "Based on what you've described, it does not really look like the typical flu pattern."
- Do NOT mention the numeric score directly in your answer.
- Explain in simple language what common flu symptoms are and compare them to the user's symptoms.
- You may briefly mention that other causes like muscle strain, tension headaches, mild viral infections or allergies are possible,
  but you MUST NOT name any specific disease as a diagnosis.

Structure your answer as 3 short paragraphs:

1) Overall assessment:
   - 2–3 sentences explaining whether flu seems likely/possible/unlikely and why (using the label and symptoms).

2) Comparison and other possibilities (non-diagnostic):
   - 2–3 sentences comparing typical flu symptoms (from the background info) with what the user reported.
   - 1 sentence mentioning that the symptoms could also be due to other common causes (e.g., muscle strain, tension, allergies),
     but only a doctor can say for sure.

3) Advice and disclaimer:
   - 1–2 sentences of basic self-care advice (rest, fluids, avoid spreading germs).
   - 1 sentence describing red-flag symptoms when they should seek urgent care
     (trouble breathing, chest pain, confusion, very high or persistent fever).
   - 1 clear sentence: "I am not a doctor and this is not a medical diagnosis.
     Please talk to a healthcare professional for real medical advice."
"""

def build_info_system_prompt() -> str:
    return """You are an educational assistant that answers general questions about seasonal influenza (flu).

Use ONLY the background information provided to you about flu (symptoms, risk groups, red flags, prevention, etc.).
Explain things in clear, simple language.

You MUST:
- Avoid giving any personal diagnosis.
- Include a brief reminder that you are not a doctor and that your answer is general information only.
"""

# ----------------------------
# Message classification helpers
# ----------------------------
def extract_name(user_text: str) -> str | None:
    # Try to find "my name is X"
    m = re.search(r"\bmy name is\s+([A-Za-z][A-Za-z\s]{0,40})", user_text, re.IGNORECASE)
    if m:
        name = m.group(1).strip().rstrip(".,!?:;")
        return name
    return None

def is_greeting(user_text: str) -> bool:
    lower = user_text.lower()
    return any(
        g in lower
        for g in ["hello", "hi ", " hi", "hey", "salam", "assalam", "assalamu alaikum", "assalamualaikum"]
    )

def looks_like_flu_question(user_text: str) -> bool:
    lower = user_text.lower()
    if "flu" in lower or "influenza" in lower:
        # e.g., "what is flu", "how does flu spread", "symptoms of flu"
        return any(q in lower for q in ["what", "how", "when", "why", "symptom", "spread", "prevent", "risk"])
    return False

# ----------------------------
# Talk to Claude with RAG (symptom mode)
# ----------------------------
def ask_flu_with_symptoms(user_text: str, symptoms: dict) -> str:
    score = flu_score(symptoms)
    label = interpret_flu_score(score)
    symptom_summary = format_symptom_summary(symptoms)

    rag_context = f"""
    === Symptom-based flu assessment ===
    Numeric flu score (0–1): {score:.2f}
    Label: {label}

    {symptom_summary}

    === Background information about flu (from WHO / CDC style sources) ===
    {RAG_CONTEXT}

    === User's symptom description ===
    {user_text}
    """

    msg = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=600,
        temperature=0.2,
        system=build_symptom_system_prompt(),
        messages=[
            {"role": "user", "content": rag_context}
        ],
    )

    parts = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)

    return "\n".join(parts)

# ----------------------------
# Talk to Claude in info / Q&A mode
# ----------------------------
def ask_flu_info(user_text: str) -> str:
    context = f"""
    === Flu background information ===
    {RAG_CONTEXT}

    === User question about flu ===
    {user_text}
    """
    msg = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        temperature=0.2,
        system=build_info_system_prompt(),
        messages=[
            {"role": "user", "content": context}
        ],
    )

    parts = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)

    return "\n".join(parts)

# ----------------------------
# Main bot logic
# ----------------------------
def ask_flu_bot(user_text: str) -> str:
    user_text = user_text.strip()
    if not user_text:
        return "Please type something so I can help you 😊"

    # 1) Check for introductions / greetings / general chat
    name = extract_name(user_text)
    if name is not None:
        return (
            f"Hello {name}! 👋\n"
            "I'm a simple flu helper bot. I can:\n"
            "- Explain what flu is and how it spreads.\n"
            "- Help you understand if your symptoms look similar to flu or not.\n\n"
            "If you'd like me to check for flu, please describe your symptoms "
            "(for example: fever, cough, sore throat, runny nose, body aches, tiredness, etc.)."
        )

    if is_greeting(user_text):
        return (
            "Hi there! 👋 I'm a flu helper bot.\n\n"
            "I can explain basic information about seasonal flu and give you an estimate "
            "of whether your symptoms look like flu or not.\n"
            "Tell me your symptoms, or ask me something like \"What are common flu symptoms?\""
        )

    # 2) Parse symptoms from text
    symptoms = parse_symptoms_from_text(user_text)

    # If no symptoms detected, maybe it's a flu question or general chat
    if not has_any_symptoms(symptoms):
        if looks_like_flu_question(user_text):
            # General flu info / Q&A with RAG
            return ask_flu_info(user_text)

        # Fallback general reply
        lower = user_text.lower()
        if "disease" in lower or "issue" in lower or "what is wrong" in lower:
            return (
                "I can't diagnose diseases or tell exactly what issue you have, "
                "but I can help you see whether your symptoms look like flu or not.\n\n"
                "Please describe your symptoms in a bit more detail (for example: "
                "do you have fever, cough, sore throat, runny or stuffy nose, body aches, tiredness, etc.)."
            )

        return (
            "I'm mainly designed to talk about seasonal flu.\n"
            "You can ask me general questions like \"What are common flu symptoms?\" or "
            "you can describe your symptoms and I’ll tell you whether they look similar to flu or not."
        )

    # 3) We have some symptoms → do flu-likelihood explanation with Claude
    return ask_flu_with_symptoms(user_text, symptoms)

# ----------------------------
# CLI main loop
# ----------------------------
def main():
    print("=== Flu RAG Chatbot (Educational Only) ===")
    print("You can chat normally (e.g., 'hi', 'my name is Ali'),")
    print("ask about flu (e.g., 'what are flu symptoms?'),")
    print("or describe your symptoms (e.g., 'I have fever and a bad cough').\n")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        user = input("You: ")
        if user.strip().lower() in {"quit", "exit"}:
            print("Bot: Take care! Remember, this is not medical advice.")
            break

        try:
            reply = ask_flu_bot(user)
            print("\nBot:\n" + reply + "\n")
        except Exception as e:
            print(f"\n[Error talking to Claude: {e}]\n")

if __name__ == "__main__":
    main()

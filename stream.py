import os
import json
import re
import textwrap
from typing import Optional, List, Dict, Any

import streamlit as st
import anthropic
import chromadb
from chromadb.utils import embedding_functions

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    st.error("ANTHROPIC_API_KEY is not set in the environment. Please set it and restart.")
    st.stop()

client = anthropic.Anthropic(api_key=API_KEY)

def load_corpus(path: str = "flu_rag_corpus.jsonl") -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Make sure flu_rag_corpus.jsonl is in the same folder as this app."
        )
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            docs.append(json.loads(line))
    return docs

@st.cache_resource(show_spinner=False)  # 🔥 no "Running get_vector_collection" message
def get_vector_collection():
    docs = load_corpus()
    chroma_client = chromadb.Client()
    embed_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = chroma_client.create_collection(
        name="flu_corpus",
        embedding_function=embed_fn,
    )

    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metadatas = [
        {
            "category": d.get("category", ""),
            "title": d.get("title", ""),
            "tags": ", ".join(d.get("tags", [])) if isinstance(d.get("tags"), list) else str(d.get("tags", "")),
        }
        for d in docs
    ]

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )
    return collection

def retrieve_docs(query: str, n_results: int = 4) -> List[Dict[str, Any]]:
    collection = get_vector_collection()
    res = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    out: List[Dict[str, Any]] = []
    if not res["ids"] or not res["ids"][0]:
        return out

    for i in range(len(res["ids"][0])):
        out.append(
            {
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i],
            }
        )
    return out

def build_rag_context_from_docs(docs: List[Dict[str, Any]]) -> str:
    chunks = []
    for d in docs:
        meta = d.get("metadata", {})
        title = meta.get("title", "")
        category = meta.get("category", "")
        header = f"[{category}] {title}".strip()
        text = d.get("text", "")
        chunk = f"{header}\n{text}" if header else text
        chunks.append(chunk)
    if not chunks:
        return "No extra background documents were retrieved."
    return "\n\n---\n\n".join(chunks)

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

def parse_symptoms_from_text(user_text: str) -> Dict[str, int]:
    symptoms = {field: 0 for field in SYMPTOM_FIELDS}
    text = user_text.lower()
    for kw, field in KEYWORD_MAP.items():
        if kw in text:
            symptoms[field] = 1
    return symptoms

def has_any_symptoms(symptoms: Dict[str, int]) -> bool:
    return any(symptoms.values())

def flu_score(symptoms: Dict[str, int]) -> float:
    score = 0.0

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

    if symptoms.get("NAUSEA", 0) or symptoms.get("VOMITING", 0) or symptoms.get("DIARRHEA", 0):
        score += 0.05

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

    score = max(0.0, min(1.0, score))
    return score

def interpret_flu_score(score: float) -> str:
    if score >= 0.7:
        return "LIKELY"
    elif score >= 0.4:
        return "POSSIBLE"
    else:
        return "UNLIKELY"

def format_symptom_summary(symptoms: Dict[str, int]) -> str:
    present = [k for k, v in symptoms.items() if v == 1]
    absent = [k for k, v in symptoms.items() if v == 0]

    def nice(lst: List[str]) -> str:
        return ", ".join(lst) if lst else "None detected from keywords."

    return textwrap.dedent(
        f"""
        Parsed symptoms from your message
        (1 = keyword detected, 0 = no keyword):

        Present (1): {nice(present)}
        Absent (0): {nice(absent)}
        """
    ).strip()

def extract_name(user_text: str) -> Optional[str]:
    m = re.search(r"\bmy name is\s+([A-Za-z][A-Za-z\s]{0,40})", user_text, re.IGNORECASE)
    if m:
        name = m.group(1).strip().rstrip(".,!?:;")
        return name
    return None

def is_greeting(user_text: str) -> bool:
    lower = user_text.lower()
    greetings = ["hello", "hi ", " hi", "hey", "salam", "assalam", "assalamu alaikum", "assalamualaikum"]
    return any(g in lower for g in greetings)

def looks_like_flu_question(user_text: str) -> bool:
    lower = user_text.lower()
    if "flu" in lower or "influenza" in lower:
        if any(q in lower for q in ["what", "how", "when", "why", "symptom", "spread", "prevent", "risk", "?"]):
            return True
    return False

def build_symptom_system_prompt() -> str:
    return """You are a cautious assistant focused on seasonal influenza (flu).

You will receive:
- A numeric flu score between 0 and 1 (from a simple rule-based model).
- A label: LIKELY / POSSIBLE / UNLIKELY.
- A summary of which symptoms were detected.
- Several retrieved background documents about flu.
- The user's original symptom description.

Your job:
- Start with ONE short sentence that qualitatively reflects the label, e.g.:
  - LIKELY   → "Based on what you've described, it seems quite likely your illness could be the flu."
  - POSSIBLE → "Based on what you've described, it's possible this could be the flu, but it's not certain."
  - UNLIKELY → "Based on what you've described, it does not really look like the typical flu pattern."
- Do NOT mention the numeric score directly in your answer.
- Explain in simple language what common flu symptoms are and compare them to the user's symptoms.
- You may briefly mention other general possibilities such as muscle strain, tension headaches,
  mild viral infections or allergies, but you MUST NOT name any specific disease as a diagnosis.

Structure your answer as 3 short paragraphs:

1) Overall assessment:
   - 2–3 sentences explaining whether flu seems likely/possible/unlikely and why (using the label and symptoms).

2) Comparison and other possibilities (non-diagnostic):
   - 2–3 sentences comparing typical flu symptoms with what the user reported.
   - 1 sentence noting that symptoms could also relate to other common causes, but only a doctor can say for sure.

3) Advice and disclaimer:
   - 1–2 sentences of basic self-care advice (rest, fluids, avoid spreading germs).
   - 1 sentence listing red-flag symptoms when they should seek urgent care
     (trouble breathing, chest pain, confusion, very high or persistent fever).
   - 1 clear sentence: "I am not a doctor and this is not a medical diagnosis.
     Please talk to a healthcare professional for real medical advice."
"""

def build_info_system_prompt() -> str:
    return """You are an assistant that answers general questions about seasonal influenza (flu).

You will receive several retrieved background documents about flu and a user question.

Use ONLY this background information to answer:
- Explain in clear, simple language.
- Do NOT provide a personal diagnosis.
- Include a brief reminder that you are not a doctor and that your answer is general information only.
"""
def ask_flu_with_symptoms(user_text: str, symptoms: Dict[str, int]) -> str:
    score = flu_score(symptoms)
    label = interpret_flu_score(score)
    symptom_summary = format_symptom_summary(symptoms)

    retrieved = retrieve_docs(user_text, n_results=5)
    rag_context = build_rag_context_from_docs(retrieved)

    prompt = f"""
    === Symptom-based flu assessment ===
    Numeric flu score (0–1): {score:.2f}
    Label: {label}

    {symptom_summary}

    === Retrieved background documents about flu ===
    {rag_context}

    === User's symptom description ===
    {user_text}
    """

    msg = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=700,
        temperature=0.2,
        system=build_symptom_system_prompt(),
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)

def ask_flu_info(user_text: str) -> str:
    retrieved = retrieve_docs(user_text, n_results=5)
    rag_context = build_rag_context_from_docs(retrieved)

    prompt = f"""
    === Retrieved background documents about flu ===
    {rag_context}

    === User question about flu ===
    {user_text}
    """

    msg = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=600,
        temperature=0.2,
        system=build_info_system_prompt(),
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)

def ask_flu_bot(user_text: str) -> str:
    user_text = user_text.strip()
    if not user_text:
        return "Please type something so I can help you 😊"

    name = extract_name(user_text)
    if name is not None:
        return (
            f"Hello {name}! 👋\n"
            "I'm a flu helper bot. I can:\n"
            "- Explain what seasonal flu is and how it spreads.\n"
            "- Describe common flu symptoms and prevention.\n"
            "- Help you understand if your symptoms look similar to flu or not.\n\n"
            "If you'd like me to check for flu, please describe your symptoms "
            "(for example: fever, cough, sore throat, runny nose, body aches, tiredness, etc.)."
        )

    if is_greeting(user_text):
        return (
            "Hi there! 👋 I'm a flu-focused chatbot.\n\n"
            "You can:\n"
            "- Ask general questions like \"What are common flu symptoms?\" or \"How does flu spread?\"\n"
            "- Describe your symptoms and I’ll tell you whether they look similar to flu or not.\n"
        )

    symptoms = parse_symptoms_from_text(user_text)

    if has_any_symptoms(symptoms):
        return ask_flu_with_symptoms(user_text, symptoms)
    if looks_like_flu_question(user_text):
        return ask_flu_info(user_text)

    lower = user_text.lower()
    if "disease" in lower or "issue" in lower or "what is wrong" in lower:
        return (
            "I can't diagnose exactly what disease you have, "
            "but I can help you see whether your symptoms resemble flu or not.\n\n"
            "Please describe your symptoms in more detail (for example: "
            "fever, cough, sore throat, runny or stuffy nose, body aches, tiredness, etc.)."
        )
    return (
        "I'm mainly designed to talk about seasonal flu.\n"
        "You can ask me things like \"What are the symptoms of flu?\" or "
        "\"How can I prevent flu?\".\n"
        "If you want me to estimate whether your symptoms look like flu, "
        "please describe what you're feeling."
    )

st.set_page_config(page_title="Flu RAG Chatbot", page_icon="🤒", layout="centered")

st.title("🤒 Flu RAG Chatbot")
st.write(
    "Chat with a flu-focused assistant. "
    "It uses a rule-based symptom checker plus a vector database of flu information, "
    "together with an AI model to explain things in natural language.\n\n"
    "**Important:** This is **not** a medical device and **not** a diagnosis. "
    "Always consult a healthcare professional for real medical advice."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I'm a flu helper bot. You can say things like:\n"
                       "- \"My name is Ali\"\n"
                       "- \"What are common flu symptoms?\"\n"
                       "- \"I have fever and cough since yesterday\""
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        try:
            reply = ask_flu_bot(user_input)
        except Exception as e:
            reply = f"Oops, something went wrong while contacting the AI model:\n\n`{e}`"
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

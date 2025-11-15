# 🤒 Flu RAG Chatbot

A simple Retrieval-Augmented Generation (RAG) chatbot that talks about **seasonal influenza (flu)** and helps you understand whether your symptoms **look similar to flu or not**.

The bot:

- Uses a **rule-based symptom checker** (fever, cough, sore throat, etc.)
- Uses a **vector database (ChromaDB)** with a small flu knowledge corpus
- Calls **Anthropic Claude** to generate natural language explanations
- Runs in a **Streamlit chat UI**

> ⚠️ **Important:** This is **not** a medical device and **not** a diagnosis tool.  
> It is only for demonstration / educational purposes. Always consult a healthcare professional for real medical advice.

---

## ✨ Features

- 💬 **Chatty interface**  
  - You can greet it (“hi”, “hello”), or say “my name is X”, and it replies like a normal chatbot.
- 🦠 **Flu symptom helper**  
  - Describe your symptoms (e.g. *“I have fever, dry cough and muscle aches since yesterday”*).  
  - The bot runs a **rule-based flu-likeness check** and explains if flu seems **likely / possible / unlikely** in words (no raw scores shown).
- 📚 **RAG over flu knowledge**  
  - A custom corpus (`flu_rag_corpus.jsonl`) with documents about:
    - Common flu symptoms
    - Flu vs cold vs allergies
    - High-risk groups
    - Red-flag/emergency symptoms
    - Prevention & self-care  
  - Stored in **ChromaDB** as a vector database, queried for each question/symptom message.
- 🧠 **Claude-powered answers**  
  - Uses the retrieved flu docs + the rule-based score as context
  - Claude generates a cautious, easy-to-understand explanation with a clear disclaimer.

---

## 🏗️ Architecture Overview

High-level pipeline:

1. **User message** comes from the Streamlit chat UI.
2. **Conversation logic:**
   - If the user says “my name is X” → friendly intro.
   - If the user greets (“hi”, “hello”) → bot explains what it can do.
   - Otherwise:
     - Symptoms are parsed with simple keyword rules (fever, cough, etc.)
     - A **flu-likeness score** (`LIKELY / POSSIBLE / UNLIKELY`) is computed.
3. **Vector DB (ChromaDB) RAG:**
   - The user’s text is used as a semantic search query.
   - Top-k flu documents are retrieved from `flu_rag_corpus.jsonl`.
4. **Claude prompt:**
   - System prompt enforces:
     - No diagnosis
     - Clear explanation of flu vs user symptoms
     - Advice + red-flag warning
   - User content includes:
     - Flu label (likely / possible / unlikely)
     - Parsed symptom summary
     - Retrieved RAG context
     - User’s original message
5. **Answer is shown** in the Streamlit chat.

So you can talk about **RAG + vector DB + rule-based scoring + LLM** in your report.

---

## 🧰 Tech Stack

- **Backend / Logic**
  - Python 3.x
  - [Anthropic Claude API](https://docs.anthropic.com/)
- **Vector Database**
  - [ChromaDB](https://www.trychroma.com/) (in-memory, local)
- **UI**
  - [Streamlit](https://streamlit.io/) chat interface
- **Embeddings**
  - `chromadb.utils.embedding_functions.DefaultEmbeddingFunction`  
    (works out of the box, good for a student/demo project)

---

## 📁 Project Structure

Typical layout:

```text
Flu-Rag-Bot/
├── flu_rag_corpus.jsonl      # Flu knowledge corpus (RAG documents)
├── streamlit_app.py          # Streamlit UI + bot logic (main entry)
├── app1.py                   # Optional CLI version (no UI, run in terminal)
└── README.md

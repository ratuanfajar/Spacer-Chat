import json
import os
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

PROMPT_PATH = Path(__file__).parent / "chat_prompt.json"


def load_prompt_config():
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"File prompt tidak ditemukan di: {PROMPT_PATH}")

    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt():
    config = load_prompt_config()

    style = "\n".join(f"- {s}" for s in config.get("style_rules", []))
    guardrails = "\n".join(f"- {g}" for g in config.get("guardrails", []))

    reasoning_steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(config.get("reasoning", {}).get("steps", [])))
    
    output_structure = "\n".join(f"- {s}" for s in config.get("output", {}).get("structure", []))
    output_rules = "\n".join(f"- {r}" for r in config.get("output", {}).get("rules", []))

    system_message = f"""
    PERSONA:
    {config.get("persona")}

    TASK:
    {config.get("task")}

    STYLE RULES:
    {style}

    GUARDRAILS:
    {guardrails}

    REASONING INSTRUCTION:
    {config.get("reasoning", {}).get("instruction")}

    STEPS REASONING:
    {reasoning_steps}

    OUTPUT STRUCTURE:
    {output_structure}

    OUTPUT RULES:
    {output_rules}

    FALLBACK:
    {config.get("fallback")}
    """

    user_template = """
    Konteks Materi:
    {context}

    Pertanyaan Mahasiswa:
    {question}
    """

    return ChatPromptTemplate.from_messages([
        ("system", system_message.strip()),
        ("human", user_template.strip())
    ])
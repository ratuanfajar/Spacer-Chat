import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.config import settings

class RAGGenerator:
    def __init__(self):
        print("Proses Generator")

        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
            temperature=0.3,
            streaming=True
        )

        # load prompt.json
        prompt_path = Path(__file__).parent / "chat_prompt.json"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_config = json.load(f)

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        rules = "\n".join(f"- {r}" for r in self.prompt_config["style_rules"])
        guardrails = "\n".join(f"- {g}" for g in self.prompt_config["guardrails"])
        reasoning_steps = "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(self.prompt_config["reasoning"]["steps"])
        )

        output_structure = "\n".join(
            f"- {r}" for r in self.prompt_config["output"]["structure"]
        )

        output_rules = "\n".join(
            f"- {r}" for r in self.prompt_config["output"]["rules"]
        )

        return f"""
        Persona: {self.prompt_config["persona"]}.
        Tugas: {self.prompt_config["task"]}

        Gaya Penjelasan:
        {rules}

        Penalaran:
        {self.prompt_config["reasoning"]["instruction"]}
        {reasoning_steps}

        Guardrails:
        {guardrails}

        Aturan Output:
        {output_rules}

        Struktur Output:
        {output_structure}

        Output HARUS berupa JSON valid:
        {{
        "content": "...",
        "suggested_questions": ["...", "..."]
        }}
        """

    def generate(self, question: str, context: str) -> Dict[str, Any]:

        user_prompt = f"""
        Konteks:
        {context}

        Pertanyaan:
        {question}
        """

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)

        raw_text = response.content.strip()

        # parsing JSON aman
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return {
                "content": raw_text,
                "suggested_questions": []
            }
        
if __name__ == "__main__":
    gen = RAGGenerator()

    result = gen.generate(
        question="Apa itu neural network?",
        context="Neural network adalah model komputasi yang terinspirasi dari otak manusia."
    )

    print(result)
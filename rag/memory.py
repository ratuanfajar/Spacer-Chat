class ChatMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history = []

    def add_turn(self, role: str, text: str):
        self.history.append({"role": role, "text": text})
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[- self.max_turns * 2 :]

    def get_context(self):
        return self.history
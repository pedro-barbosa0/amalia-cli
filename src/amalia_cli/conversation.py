class Conversation:
    def __init__(self, system_prompt: str | None = None):
        self.messages: list[dict] = []

        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt,
            })

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content,
        })

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content,
        })

    def get_messages(self) -> list[dict]:
        return self.messages.copy()

    def clear(self):
        self.messages.clear()
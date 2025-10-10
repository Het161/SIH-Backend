from transformers import pipeline, set_seed

class AIChatbot:
    def __init__(self):
        self.generator = pipeline('text-generation', model='microsoft/DialoGPT-medium')
        set_seed(42)
    
    def chat(self, user_input: str) -> str:
        outputs = self.generator(user_input, max_length=100, num_return_sequences=1)
        return outputs[0]['generated_text']

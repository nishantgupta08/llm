from transformers import pipeline

class EncoderDecoder:
    def __init__(self, model_name: str, task: str = "summarization", temperature: float = 0.7):
        self.model_name = model_name
        self.task = task
        self.temperature = temperature
        self.pipeline = pipeline(task=self.task, model=self.model_name)

    def run(self, text: str, max_input_length: int = 1024) -> str:
        input_text = text[:max_input_length]  # truncate if needed
        output = self.pipeline(input_text, do_sample=True, temperature=self.temperature)
        return output[0]['summary_text'] if 'summary_text' in output[0] else output[0]['generated_text']
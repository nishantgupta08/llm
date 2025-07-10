from transformers import pipeline
from langchain.llms import HuggingFacePipeline

class LangchainDecoder:
    def __init__(self, model_name: str, temperature: float = 0.7, max_length: int = 128, top_k: int = 50, top_p: float = 1.0):
        self.model_name = model_name
        self.temperature = temperature
        self.max_length = max_length
        self.top_k = top_k
        self.top_p = top_p

    def get_llm(self):
        kwargs = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_length": self.max_length,
            "top_k": self.top_k,
            "top_p": self.top_p,
        }
        pipe = pipeline("text-generation", **kwargs)
        return HuggingFacePipeline(pipeline=pipe)

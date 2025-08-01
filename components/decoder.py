# decoder.py

from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from typing import Any, Dict


class LangchainDecoder:
    """
    A LangChain-compatible decoder using HuggingFace text-generation pipeline.
    Supports flexible decoding strategies via kwargs.
    """

    def __init__(self, model_name: str, **decoding_params: Dict[str, Any]):
        """
        Initialize the text generation pipeline.

        Args:
            model_name (str): HuggingFace model name or path.
            decoding_params (dict): Parameters like temperature, max_new_tokens, top_p, etc.
        """
        self.model_name = model_name
        self.decoding_params = decoding_params or {}

        try:
            self.pipeline = pipeline(
                task="text-generation",
                model=self.model_name,
                **self.decoding_params
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize HuggingFace pipeline: {e}")

    def run(self, prompt: str) -> str:
        """
        Generate text for a given prompt using the pipeline.

        Args:
            prompt (str): Input prompt for generation.

        Returns:
            str: Generated text.
        """
        try:
            outputs = self.pipeline(prompt)
            return outputs[0].get("generated_text", "")
        except Exception as e:
            raise RuntimeError(f"Text generation failed: {e}")

    def get_llm(self) -> Any:
        """
        Return the LangChain-wrapped HuggingFace pipeline (for use in LangChain chains).

        Returns:
            HuggingFacePipeline: LangChain-compatible LLM interface.
        """
        return HuggingFacePipeline(pipeline=self.pipeline)

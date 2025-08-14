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

        # Filter out unsupported parameters
        filtered_params = self._filter_supported_params(self.decoding_params)

        try:
            self.pipeline = pipeline(
                task="text-generation",
                model=self.model_name,
                **filtered_params
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize HuggingFace pipeline: {e}")

    def _filter_supported_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out parameters that are not supported by HuggingFace text-generation pipeline.
        
        Args:
            params (dict): All decoding parameters
            
        Returns:
            dict: Filtered parameters that are supported by the pipeline
        """
        # Standard parameters supported by most text-generation models
        supported_params = {
            'temperature', 'top_p', 'top_k', 'repetition_penalty', 'length_penalty',
            'no_repeat_ngram_size', 'max_new_tokens', 'min_length', 'max_length',
            'num_beams', 'early_stopping', 'do_sample', 'typical_p', 'penalty_alpha',
            'pad_token_id', 'eos_token_id', 'bos_token_id', 'unk_token_id',
            'attention_mask', 'use_cache', 'return_dict_in_generate'
        }
        
        # Filter parameters
        filtered = {}
        unsupported = []
        
        for key, value in params.items():
            if key in supported_params:
                filtered[key] = value
            else:
                unsupported.append(key)
        
        if unsupported:
            print(f"Warning: The following parameters are not supported by the text-generation pipeline and will be ignored: {unsupported}")
        
        return filtered

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

# encoder.py

from langchain.embeddings import HuggingFaceEmbeddings
import torch
import numpy as np
from typing import Optional, List, Union, Any, Dict


class LangchainEncoder:
    """
    A unified encoder compatible with LangChain's vector store,
    supporting normalization and pooling strategies via encoding_params.
    """

    def __init__(
        self,
        model_name: str,
        **encoding_params: Optional[Dict[str, Any]]
    ):
        """
        Args:
            model_name (str): HuggingFace model ID or path.
            encoding_params (dict): Custom params like pooling, normalization, device, etc.
        """
        self.model_name = model_name

        # Defaults
        defaults = {
            "pooling": "mean",
            "normalize": "none",
            "layer": -1,
            "device": "cuda" if torch.cuda.is_available() else "cpu"
        }

        # Merge defaults with passed encoding params
        self.encoding_params = {**defaults, **(encoding_params or {})}

        self.pooling = self.encoding_params["pooling"]
        self.normalization = self.encoding_params["normalize"]
        self.layer = self.encoding_params["layer"]
        self.device = self.encoding_params["device"]

        allowed_normalizations = {"none", "l2", "l1", "max", "zscore", "minmax"}
        if self.normalization not in allowed_normalizations:
            raise ValueError(f"Unsupported normalization: '{self.normalization}'")

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={
                "trust_remote_code": False,
                "device": self.device
            },
            encode_kwargs={
                "normalize_embeddings": True  # Keeps HF's internal norm; your norm applies after
            }
        )
        
        # Move model to device after loading to avoid meta tensor issues
        if hasattr(self.embedding_model, 'client') and hasattr(self.embedding_model.client, 'model'):
            try:
                if self.device == "cuda" and torch.cuda.is_available():
                    # Use to_empty() for meta tensors, to() for regular tensors
                    if hasattr(self.embedding_model.client.model, 'to_empty'):
                        self.embedding_model.client.model = self.embedding_model.client.model.to_empty("cuda")
                    else:
                        self.embedding_model.client.model = self.embedding_model.client.model.to("cuda")
                else:
                    if hasattr(self.embedding_model.client.model, 'to_empty'):
                        self.embedding_model.client.model = self.embedding_model.client.model.to_empty("cpu")
                    else:
                        self.embedding_model.client.model = self.embedding_model.client.model.to("cpu")
            except Exception as e:
                # If device placement fails, continue with default device
                print(f"Warning: Could not move model to {self.device}: {e}")

    def _apply_normalization(self, embeddings: List[List[float]]) -> List[List[float]]:
        if self.normalization == "none":
            return embeddings

        embeddings_np = np.array(embeddings)

        if self.normalization == "l2":
            norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
            embeddings_np /= (norms + 1e-8)
        elif self.normalization == "l1":
            norms = np.sum(np.abs(embeddings_np), axis=1, keepdims=True)
            embeddings_np /= (norms + 1e-8)
        elif self.normalization == "max":
            max_vals = np.max(np.abs(embeddings_np), axis=1, keepdims=True)
            embeddings_np /= (max_vals + 1e-8)
        elif self.normalization == "zscore":
            mean = np.mean(embeddings_np, axis=1, keepdims=True)
            std = np.std(embeddings_np, axis=1, keepdims=True)
            embeddings_np = (embeddings_np - mean) / (std + 1e-8)
        elif self.normalization == "minmax":
            min_vals = np.min(embeddings_np, axis=1, keepdims=True)
            max_vals = np.max(embeddings_np, axis=1, keepdims=True)
            embeddings_np = (embeddings_np - min_vals) / (max_vals - min_vals + 1e-8)

        return embeddings_np.tolist()

    def run(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Encode a string or list of strings with optional post-normalization.
        """
        try:
            if isinstance(text, str):
                embedding = self.embedding_model.embed_query(text)
                return self._apply_normalization([embedding])[0]
            elif isinstance(text, list):
                embeddings = self.embedding_model.embed_documents(text)
                return self._apply_normalization(embeddings)
            else:
                raise TypeError("Input must be a string or a list of strings.")
        except Exception as e:
            raise RuntimeError(f"Encoding failed: {e}")

    def get_encoder(self) -> Any:
        """
        Return the underlying LangChain-compatible encoder object.
        """
        return self.embedding_model

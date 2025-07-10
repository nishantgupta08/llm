from langchain.embeddings import HuggingFaceEmbeddings

class LangchainEncoder:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def get_embeddings(self):
        return HuggingFaceEmbeddings(model_name=self.model_name)

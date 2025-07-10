from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class VectorStoreBuilder:
    def __init__(self, encoder_model: str):
        self.embeddings = HuggingFaceEmbeddings(model_name=encoder_model)

    def build_vectorstore(self, texts: list):
        return FAISS.from_texts(texts, embedding=self.embeddings)

    def get_retriever(self, texts: list, k: int):
        vectorstore = self.build_vectorstore(texts)
        return vectorstore.as_retriever(search_kwargs={"k": k})

from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class InMemoryRAG:
    def __init__(self) -> None:
        self.docs: List[str] = []
        self.doc_ids: List[str] = []
        self.vectorizer = TfidfVectorizer(max_features=4096)
        self.matrix = None

    def index(self, doc_ids: List[str], documents: List[str]) -> None:
        self.doc_ids = doc_ids
        self.docs = documents
        self.matrix = self.vectorizer.fit_transform(self.docs)

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        if not self.docs:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.doc_ids[i], self.docs[i], float(scores[i])) for i, _ in ranked]


rag = InMemoryRAG()


def rebuild_from_db(rows: List[Tuple[str, str]]) -> None:
    if not rows:
        rag.index([], [])
        return
    doc_ids = [r[0] for r in rows]
    documents = [r[1] for r in rows]
    rag.index(doc_ids, documents)



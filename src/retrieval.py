from typing import Any, Dict, List

import bm25s


def build_index(chunks: List[Dict[str, Any]], index_path: str) -> None:
    """Construye el indice BM25 sobre los chunks y lo guarda en disco."""
    textos = [c["text"] for c in chunks]
    corpus_tokens = bm25s.tokenize(textos, stopwords="en", show_progress=False)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens, show_progress=False)
    retriever.save(index_path, corpus=chunks)


def load_index(index_path: str) -> bm25s.BM25:
    """Carga un indice BM25 ya construido, con su corpus incluido."""
    return bm25s.BM25.load(index_path, load_corpus=True)


def search_index(retriever: bm25s.BM25, query: str,
                  k: int) -> List[Dict[str, Any]]:
    """Busca una query en el indice y devuelve los k chunks mas relevantes."""
    query_tokens = bm25s.tokenize(query, stopwords="en", show_progress=False)
    results, scores = retriever.retrieve(query_tokens, k=k, show_progress=False)
    return list(results[0])
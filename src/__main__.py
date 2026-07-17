import fire


class Rag:
    """CLI del proyecto RAG against the machine."""

    def index(self, max_chunk_size: int = 2000) -> None:
        """Ingesta y crea el indice del repositorio."""
        print(f"TODO: index con max_chunk_size={max_chunk_size}")

    def search(self, query: str, k: int = 10) -> None:
        """Busca una unica pregunta."""
        print(f"TODO: search '{query}' con k={k}")

    def search_dataset(
        self,
        dataset_path: str,
        k: int = 10,
        save_directory: str = "data/output/search_results",
    ) -> None:
        """Busca todas las preguntas de un dataset JSON."""
        print(f"TODO: search_dataset {dataset_path} "
              f"k={k} -> {save_directory}")

    def answer_dataset(
        self,
        search_results_path: str,
        save_directory: str = "data/output/answers",
    ) -> None:
        """Genera respuestas a partir de resultados de busqueda."""
        print(f"TODO: answer_dataset {search_results_path} "
              f"-> {save_directory}")

    def evaluate(
        self, search_results_path: str, ground_truth_path: str
    ) -> None:
        """Evalua resultados de busqueda contra el ground truth."""
        print(f"TODO: evaluate {search_results_path} "
              f"vs {ground_truth_path}")

    def answer(self, query: str, k: int = 10) -> None:
        """Responde una pregunta unica con contexto recuperado."""
        print(f"TODO: answer '{query}' con k={k}")


if __name__ == "__main__":
    fire.Fire(Rag)

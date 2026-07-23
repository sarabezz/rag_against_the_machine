import time
from pathlib import Path
from typing import List

from tqdm import tqdm

from src.chunking import CodeChunk, chunk_markdown_source, chunk_python_source


def build_chunks(repo_root: str, max_chunk_size: int = 2000) -> List[CodeChunk]:
    """Recorre el repositorio, aplica el chunker correcto segun la
    extension de cada archivo, y devuelve todos los chunks."""
    root = Path(repo_root)
    files = [p for p in root.rglob("*")
             if p.suffix in (".py", ".md") and p.is_file()]

    all_chunks: List[CodeChunk] = []
    errores = 0

    for path in tqdm(files, desc="Indexando"):
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            print(f"AVISO: no se pudo leer {path}: {exc}")
            errores += 1
            continue

        file_path = str(path)
        try:
            if path.suffix == ".py":
                chunks = chunk_python_source(source, file_path,
                                              max_chunk_size)
            else:
                chunks = chunk_markdown_source(source, file_path,
                                                max_chunk_size)
        except SyntaxError:
            chunks = chunk_markdown_source(source, file_path,
                                            max_chunk_size)
            errores += 1

        all_chunks.extend(chunks)

    print(f"Archivos procesados: {len(files)} | errores de parseo: {errores}")
    return all_chunks
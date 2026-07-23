import ast
import re
from typing import List, NamedTuple, Tuple


class CodeChunk(NamedTuple):
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str


def _split_block(text: str, max_chunk_size: int) -> List[Tuple[int, int]]:
    """Parte un bloque de texto en trozos <= max_chunk_size, cortando por
    lineas completas cuando se puede, y por caracteres como ultimo recurso
    si una sola linea ya supera el limite."""
    if len(text) <= max_chunk_size:
        return [(0, len(text))]
    result: List[Tuple[int, int]] = []
    lines = text.splitlines(keepends=True)
    cur_start = 0
    cur_len = 0
    for line in lines:
        if len(line) > max_chunk_size:
            if cur_len > 0:
                result.append((cur_start, cur_start + cur_len))
                cur_start += cur_len
                cur_len = 0
            pos = 0
            while pos < len(line):
                piece_end = min(pos + max_chunk_size, len(line))
                result.append((cur_start + pos, cur_start + piece_end))
                pos = piece_end
            cur_start += len(line)
            continue
        if cur_len + len(line) > max_chunk_size and cur_len > 0:
            result.append((cur_start, cur_start + cur_len))
            cur_start += cur_len
            cur_len = 0
        cur_len += len(line)
    if cur_len > 0:
        result.append((cur_start, cur_start + cur_len))
    return result


def _emit_chunks(source: str, file_path: str, start_char: int,
                  end_char: int, max_chunk_size: int) -> List[CodeChunk]:
    """Convierte un bloque [start_char, end_char) en chunks, filtrando
    trozos vacios o solo espacios en blanco."""
    block = source[start_char:end_char]
    out: List[CodeChunk] = []
    for s_off, e_off in _split_block(block, max_chunk_size):
        s, e = start_char + s_off, start_char + e_off
        text = source[s:e]
        if not text.strip():
            continue
        out.append(CodeChunk(file_path, s, e, text))
    return out


def chunk_python_source(source: str, file_path: str,
                         max_chunk_size: int = 2000) -> List[CodeChunk]:
    tree = ast.parse(source)
    lines = source.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def char_range(start_line: int, end_line: int) -> Tuple[int, int]:
        start_char = line_offsets[start_line - 1]
        end_char = min(line_offsets[end_line], len(source))
        return start_char, end_char

    segments: List[Tuple[int, int]] = []
    buffer_start = 1
    for node in tree.body:
        is_def = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                    ast.ClassDef))
        if is_def:
            if node.lineno > buffer_start:
                segments.append((buffer_start, node.lineno - 1))
            segments.append((node.lineno, node.end_lineno))
            buffer_start = node.end_lineno + 1
    if buffer_start <= len(lines):
        segments.append((buffer_start, len(lines)))

    chunks: List[CodeChunk] = []
    for start_line, end_line in segments:
        if end_line < start_line:
            continue
        start_char, end_char = char_range(start_line, end_line)
        chunks.extend(_emit_chunks(source, file_path, start_char,
                                    end_char, max_chunk_size))
    return chunks


def chunk_markdown_source(source: str, file_path: str,
                           max_chunk_size: int = 2000) -> List[CodeChunk]:
    lines = source.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    header_line_indices = [i for i, line in enumerate(lines)
                            if re.match(r"^#{1,6}\s", line)]
    section_starts = sorted(set([0] + header_line_indices))

    chunks: List[CodeChunk] = []
    for i, start_idx in enumerate(section_starts):
        end_idx = (section_starts[i + 1] if i + 1 < len(section_starts)
                   else len(lines))
        start_char = line_offsets[start_idx]
        end_char = min(line_offsets[end_idx], len(source))
        chunks.extend(_emit_chunks(source, file_path, start_char,
                                    end_char, max_chunk_size))
    return chunks
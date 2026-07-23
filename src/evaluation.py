from statistics import mean
from typing import Any, Dict, List


def overlap_ratio(retrieved: Dict[str, Any],
                   true_source: Dict[str, Any]) -> float:
    """Que porcentaje de la fuente correcta queda cubierto por lo
    que se recupero. 0.0 si son archivos distintos."""
    if retrieved["file_path"] != true_source["file_path"]:
        return 0.0
    r_start = retrieved["first_character_index"]
    r_end = retrieved["last_character_index"]
    t_start = true_source["first_character_index"]
    t_end = true_source["last_character_index"]
    overlap = max(0, min(r_end, t_end) - max(r_start, t_start))
    true_len = max(1, t_end - t_start)
    return overlap / true_len


def is_found(true_source: Dict[str, Any],
             retrieved_sources: List[Dict[str, Any]],
             threshold: float = 0.05) -> bool:
    return any(overlap_ratio(r, true_source) >= threshold
               for r in retrieved_sources)


def evaluate_recall(search_results: Dict[str, Any],
                     ground_truth: Dict[str, Any],
                     threshold: float = 0.05) -> Dict[str, Any]:
    """Calcula el recall@k por pregunta, y lo agrupa por dificultad."""
    predicted_by_id = {r["question_id"]: r
                        for r in search_results["search_results"]}

    scores: List[float] = []
    scores_by_difficulty: Dict[str, List[float]] = {}

    for gt_q in ground_truth["rag_questions"]:
        qid = gt_q["question_id"]
        pred = predicted_by_id.get(qid)
        retrieved = pred["retrieved_sources"] if pred else []

        found = sum(1 for src in gt_q["sources"]
                    if is_found(src, retrieved, threshold))
        total = max(1, len(gt_q["sources"]))
        score = found / total
        scores.append(score)

        diff = gt_q.get("difficulty", "unknown")
        scores_by_difficulty.setdefault(diff, []).append(score)

    return {
        "num_questions": len(scores),
        "recall_at_k": mean(scores) if scores else 0.0,
        "recall_by_difficulty": {
            diff: mean(vals) for diff, vals in scores_by_difficulty.items()
        },
    }
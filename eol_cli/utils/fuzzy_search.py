"""Fuzzy search utilities for finding similar product names."""


def _get_ngrams(s: str, n: int) -> set[str]:
    """Generate character n-grams from *s*.

    Returns an empty set when ``len(s) < n`` (no complete n-gram fits).
    """
    s = s.lower()
    return {s[i : i + n] for i in range(len(s) - n + 1)}


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        The minimum number of single-character edits required to change s1 into s2
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _jaccard_similarity(s1: str, s2: str, n: int = 2) -> float:
    """Calculate Jaccard similarity between two strings using n-grams.

    Args:
        s1: First string
        s2: Second string
        n: Size of n-grams (default: 2 for bigrams)

    Returns:
        Jaccard similarity score between 0 and 1
    """
    if not s1 or not s2:
        return 0.0

    ngrams1 = _get_ngrams(s1, n)
    ngrams2 = _get_ngrams(s2, n)

    if not ngrams1 or not ngrams2:
        return 0.0

    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2

    return len(intersection) / len(union) if union else 0.0


def _combined_similarity(query: str, candidate: str) -> float:
    """Calculate combined similarity score using multiple metrics.

    Args:
        query: The search query
        candidate: The candidate product name

    Returns:
        Combined similarity score between 0 and 1
    """
    query_lower = query.lower()
    candidate_lower = candidate.lower()

    # Exact substring match gets highest score
    if query_lower in candidate_lower:
        # Bonus for exact match at start
        if candidate_lower.startswith(query_lower):
            return 0.95 + (0.05 * (len(query) / len(candidate)))
        return 0.85 + (0.10 * (len(query) / len(candidate)))

    # Calculate normalized Levenshtein similarity
    max_len = max(len(query_lower), len(candidate_lower))
    levenshtein_sim = 1 - (_levenshtein_distance(query_lower, candidate_lower) / max_len)

    # Calculate Jaccard similarity
    jaccard_sim = _jaccard_similarity(query_lower, candidate_lower)

    # Weighted combination (favor Levenshtein for short strings, Jaccard for longer)
    if max_len < 6:
        return 0.7 * levenshtein_sim + 0.3 * jaccard_sim
    else:
        return 0.5 * levenshtein_sim + 0.5 * jaccard_sim


def find_similar_products(
    query: str, all_products: list[str], threshold: float = 0.3, max_results: int = 5
) -> list[tuple[str, float]]:
    """Find similar product names using fuzzy matching.

    Args:
        query: The product name that was not found
        all_products: List of all available product names
        threshold: Minimum similarity score to include (0-1, default: 0.3)
        max_results: Maximum number of suggestions to return (default: 5)

    Returns:
        List of tuples (product_name, similarity_score) sorted by score (highest first)
    """
    if not query or not all_products:
        return []

    # Calculate similarity scores for all products
    scores = []
    for product in all_products:
        similarity = _combined_similarity(query, product)
        if similarity >= threshold:
            scores.append((product, similarity))

    # Sort by similarity (highest first) and limit results
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:max_results]

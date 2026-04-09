"""Unit tests for fuzzy search functionality."""

from eol_cli.utils.fuzzy_search import (
    _combined_similarity,
    _jaccard_similarity,
    _levenshtein_distance,
    find_similar_products,
)


class TestLevenshteinDistance:
    """Tests for Levenshtein distance calculation."""

    def test_identical_strings(self):
        """Test Levenshtein distance for identical strings."""
        if not (_levenshtein_distance("hello", "hello") == 0):
            raise AssertionError
        if not (_levenshtein_distance("python", "python") == 0):
            raise AssertionError

    def test_empty_string(self):
        """Test Levenshtein distance with empty strings."""
        if not (_levenshtein_distance("", "hello") == 5):
            raise AssertionError
        if not (_levenshtein_distance("hello", "") == 5):
            raise AssertionError
        if not (_levenshtein_distance("", "") == 0):
            raise AssertionError

    def test_single_character_difference(self):
        """Test Levenshtein distance with one character difference."""
        if not (_levenshtein_distance("kitten", "sitten") == 1):
            raise AssertionError
        if not (_levenshtein_distance("hello", "helo") == 1):
            raise AssertionError
        if not (_levenshtein_distance("hello", "helllo") == 1):
            raise AssertionError

    def test_multiple_differences(self):
        """Test Levenshtein distance with multiple differences."""
        if not (_levenshtein_distance("saturday", "sunday") == 3):
            raise AssertionError
        if not (_levenshtein_distance("window", "windows") == 1):
            raise AssertionError

    def test_completely_different(self):
        """Test Levenshtein distance for completely different strings."""
        distance = _levenshtein_distance("abc", "xyz")
        if not (distance == 3):
            raise AssertionError


class TestJaccardSimilarity:
    """Tests for Jaccard similarity calculation."""

    def test_identical_strings(self):
        """Test Jaccard similarity for identical strings."""
        if not (_jaccard_similarity("hello", "hello") == 1.0):
            raise AssertionError
        if not (_jaccard_similarity("python", "python") == 1.0):
            raise AssertionError

    def test_empty_strings(self):
        """Test Jaccard similarity with empty strings."""
        if not (_jaccard_similarity("", "hello") == 0.0):
            raise AssertionError
        if not (_jaccard_similarity("hello", "") == 0.0):
            raise AssertionError
        if not (_jaccard_similarity("", "") == 0.0):
            raise AssertionError

    def test_similar_strings(self):
        """Test Jaccard similarity for similar strings."""
        similarity = _jaccard_similarity("window", "windows")
        if not (0.5 < similarity < 1.0):
            raise AssertionError

    def test_completely_different(self):
        """Test Jaccard similarity for different strings."""
        similarity = _jaccard_similarity("abc", "xyz")
        if not (similarity == 0.0):
            raise AssertionError

    def test_case_insensitive(self):
        """Test that Jaccard similarity is case insensitive."""
        if not (_jaccard_similarity("Hello", "hello") == 1.0):
            raise AssertionError
        if not (_jaccard_similarity("WINDOWS", "windows") == 1.0):
            raise AssertionError

    def test_single_character_strings(self):
        """Test Jaccard similarity with single character strings (shorter than bigram n=2).

        With the fix, single-char strings use character sets as fallback,
        so identical single-char strings now have similarity 1.0.
        """
        similarity = _jaccard_similarity("a", "a")
        if not (similarity == 1.0):
            raise AssertionError
        similarity_diff = _jaccard_similarity("a", "b")
        if not (similarity_diff == 0.0):
            raise AssertionError


class TestCombinedSimilarity:
    """Tests for combined similarity calculation."""

    def test_identical_strings(self):
        """Test combined similarity for identical strings."""
        score = _combined_similarity("hello", "hello")
        if not (score > 0.95):
            raise AssertionError

    def test_substring_match(self):
        """Test combined similarity for substring matches."""
        score = _combined_similarity("window", "windows")
        if not (score > 0.85):
            raise AssertionError
        if not (score < 1.0):
            raise AssertionError

    def test_prefix_match(self):
        """Test combined similarity for prefix matches."""
        score_prefix = _combined_similarity("wind", "windows")
        score_middle = _combined_similarity("dows", "windows")
        if not (score_prefix > score_middle):
            raise AssertionError

    def test_case_insensitive(self):
        """Test that combined similarity is case insensitive."""
        score_lower = _combined_similarity("window", "windows")
        score_upper = _combined_similarity("WINDOW", "WINDOWS")
        if not (abs(score_lower - score_upper) < 0.01):
            raise AssertionError

    def test_short_strings(self):
        """Test combined similarity favors Levenshtein for short strings."""
        # For strings < 6 chars, Levenshtein should be weighted more
        score = _combined_similarity("py", "python")
        if not (0.0 < score < 1.0):
            raise AssertionError

    def test_long_strings(self):
        """Test combined similarity balances metrics for long strings."""
        # For strings >= 6 chars, equal weight
        score = _combined_similarity("apache-http", "apache-https")
        if not (0.5 < score < 1.0):
            raise AssertionError

    def test_completely_different(self):
        """Test combined similarity for different strings."""
        score = _combined_similarity("abc", "xyz")
        if not (score < 0.5):
            raise AssertionError


class TestFindSimilarProducts:
    """Tests for find_similar_products function."""

    def test_exact_match(self):
        """Test finding products with exact match."""
        products = ["windows", "linux", "macos"]
        results = find_similar_products("windows", products)
        if not (len(results) > 0):
            raise AssertionError
        if not (results[0][0] == "windows"):
            raise AssertionError
        if not (results[0][1] > 0.99):
            raise AssertionError

    def test_typo_detection(self):
        """Test finding products with typos."""
        products = ["windows", "windows-server", "linux", "macos"]
        results = find_similar_products("window", products)
        if not (len(results) > 0):
            raise AssertionError
        if "windows" not in [r[0] for r in results]:
            raise AssertionError
        # Windows should have high similarity
        windows_score = next(r[1] for r in results if r[0] == "windows")
        if not (windows_score > 0.8):
            raise AssertionError

    def test_partial_match(self):
        """Test finding products with partial matches."""
        products = ["python", "python-3", "python-2", "ruby"]
        results = find_similar_products("pythn", products)
        if not (len(results) > 0):
            raise AssertionError
        # Should find python-related products
        if not (any("python" in r[0] for r in results)):
            raise AssertionError

    def test_threshold_filtering(self):
        """Test that threshold filters out low similarity products."""
        products = ["windows", "linux", "macos", "abc", "xyz"]
        results = find_similar_products("window", products, threshold=0.5)
        # Should not include products with very low similarity
        scores = [r[1] for r in results]
        if not (all(score >= 0.5 for score in scores)):
            raise AssertionError

    def test_max_results_limit(self):
        """Test that max_results limits the number of suggestions."""
        products = [
            "windows",
            "windows-server",
            "windows-embedded",
            "windows-powershell",
            "windows-nano",
            "windows-10",
        ]
        results = find_similar_products("window", products, max_results=3)
        if not (len(results) <= 3):
            raise AssertionError

    def test_empty_product_list(self):
        """Test handling empty product list."""
        results = find_similar_products("window", [])
        if not (results == []):
            raise AssertionError

    def test_empty_query(self):
        """Test handling empty query string."""
        products = ["windows", "linux"]
        results = find_similar_products("", products)
        if not (results == []):
            raise AssertionError

    def test_results_sorted_by_similarity(self):
        """Test that results are sorted by similarity score."""
        products = ["windows", "windows-server", "linux", "wins"]
        results = find_similar_products("window", products)
        scores = [r[1] for r in results]
        # Check that scores are in descending order
        if not (scores == sorted(scores, reverse=True)):
            raise AssertionError

    def test_real_world_example(self):
        """Test with real-world product names."""
        products = [
            "ubuntu",
            "ubuntu-linux",
            "debian",
            "centos",
            "bun",
            "grunt",
            "ant",
        ]
        results = find_similar_products("ubunt", products)
        if not (len(results) > 0):
            raise AssertionError
        # Ubuntu should be the top match
        if not (results[0][0] == "ubuntu"):
            raise AssertionError
        if not (results[0][1] > 0.9):
            raise AssertionError

    def test_no_matches_above_threshold(self):
        """Test when no products match above threshold."""
        products = ["windows", "linux", "macos"]
        results = find_similar_products("zzzzz", products, threshold=0.8)
        # Might return empty or very few results
        if not (len(results) <= 1):
            raise AssertionError

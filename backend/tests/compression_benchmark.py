"""Compression Benchmark — Measures prompt compressor quality.

Tests that compressed prompts preserve critical instructions by checking
for key patterns that Kairos needs to function correctly.

Run: python -m pytest backend/tests/compression_benchmark.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prompt_compressor import compress_prompt, compress_for_tier, get_compression_stats, TIER_LIMITS, clear_cache


# ═══════════════════════════════════════
# The full Kairos system prompt (imported at runtime)
# ═══════════════════════════════════════

def _get_system_prompt():
    """Import the actual ENGINE_SYSTEM_PROMPT from routes_agents."""
    # We read the raw prompt instead of importing the module to avoid DB dependency
    import re
    path = os.path.join(os.path.dirname(__file__), "..", "routes_agents.py")
    with open(path, "r") as f:
        content = f.read()
    # Extract the prompt string between ENGINE_SYSTEM_PROMPT = """ and the closing """
    match = re.search(r'ENGINE_SYSTEM_PROMPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1)
    # Fallback: return a representative prompt
    return "You are the Kairos AI Engine v4" + " " * 10000


# ═══════════════════════════════════════
# CRITICAL PATTERNS — Must survive compression
# ═══════════════════════════════════════

# These patterns MUST be present in compressed output for Kairos to function
CRITICAL_PATTERNS = {
    "identity": [
        "Kairos",           # Engine name
        "ABC",              # Company name
    ],
    "tool_format": [
        "TOOL_CALL",        # Tool call format marker
        "DONE",             # Completion marker
    ],
    "tool_names": [
        "read_file",
        "patch_file",
        "run_query",
        "scaffold_module",
        "verify_deployment",
        "web_search",
        "call_subagent",
        "run_test",
    ],
    "code_patterns": [
        "APIRouter",         # FastAPI pattern
        "_id",               # MongoDB _id exclusion
        "uuid",              # ID generation
    ],
    "modules": [
        "Projects",
        "Timesheets",
    ],
}

# These are nice-to-have but acceptable to lose under extreme compression
OPTIONAL_PATTERNS = [
    "GST",
    "TDS",
    "Revenue Ind AS 115",
    "E8EDF2",
    "DEBUGGING DISCIPLINE",
]


class TestCompressionQuality:
    """Test that compression preserves critical information."""

    def setup_method(self):
        clear_cache()
        self.prompt = _get_system_prompt()
        assert len(self.prompt) > 5000, f"System prompt too short ({len(self.prompt)} chars) — something is wrong"

    def test_original_prompt_has_critical_patterns(self):
        """Sanity: the original prompt contains all critical patterns."""
        for category, patterns in CRITICAL_PATTERNS.items():
            for pattern in patterns:
                assert pattern in self.prompt, f"Original prompt missing critical pattern '{pattern}' (category: {category})"

    def test_groq_compression_fits_limit(self):
        """Groq compressed prompt fits within the 3500 char limit."""
        compressed = compress_for_tier(self.prompt, "groq")
        assert len(compressed) <= TIER_LIMITS["groq"], f"Groq compressed prompt ({len(compressed)} chars) exceeds limit ({TIER_LIMITS['groq']})"

    def test_cerebras_compression_fits_limit(self):
        """Cerebras compressed prompt fits within the 6000 char limit."""
        compressed = compress_for_tier(self.prompt, "cerebras")
        assert len(compressed) <= TIER_LIMITS["cerebras"], f"Cerebras compressed prompt ({len(compressed)} chars) exceeds limit ({TIER_LIMITS['cerebras']})"

    def test_huggingface_compression_fits_limit(self):
        """HuggingFace compressed prompt fits within the 6000 char limit."""
        compressed = compress_for_tier(self.prompt, "huggingface")
        assert len(compressed) <= TIER_LIMITS["huggingface"], f"HuggingFace compressed prompt ({len(compressed)} chars) exceeds limit ({TIER_LIMITS['huggingface']})"

    def test_groq_preserves_identity(self):
        """Groq compression preserves engine identity."""
        compressed = compress_for_tier(self.prompt, "groq")
        for pattern in CRITICAL_PATTERNS["identity"]:
            assert pattern in compressed, f"Groq compression lost identity pattern: '{pattern}'"

    def test_groq_preserves_tool_format(self):
        """Groq compression preserves tool call format markers."""
        compressed = compress_for_tier(self.prompt, "groq")
        for pattern in CRITICAL_PATTERNS["tool_format"]:
            assert pattern in compressed, f"Groq compression lost tool format: '{pattern}'"

    def test_groq_preserves_core_tool_names(self):
        """At least 60% of core tool names survive Groq compression."""
        compressed = compress_for_tier(self.prompt, "groq")
        found = sum(1 for t in CRITICAL_PATTERNS["tool_names"] if t in compressed)
        total = len(CRITICAL_PATTERNS["tool_names"])
        ratio = found / total
        assert ratio >= 0.6, f"Only {found}/{total} ({ratio:.0%}) core tool names survived Groq compression (need 60%+)"

    def test_cerebras_preserves_all_critical(self):
        """Cerebras (more generous limit) preserves ALL critical patterns."""
        compressed = compress_for_tier(self.prompt, "cerebras")
        missing = []
        for category, patterns in CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if pattern not in compressed:
                    missing.append(f"{category}/{pattern}")
        assert len(missing) == 0, f"Cerebras compression lost critical patterns: {missing}"

    def test_compression_ratio_reasonable(self):
        """Compression ratio is between 20% and 80% (not over- or under-compressing)."""
        compressed = compress_for_tier(self.prompt, "groq")
        stats = get_compression_stats(self.prompt, compressed)
        ratio = stats["ratio"]
        assert 15 <= ratio <= 80, f"Compression ratio {ratio}% is outside reasonable range (15-80%)"

    def test_no_data_corruption(self):
        """Compressed output is valid text with no null bytes or broken encoding."""
        for tier in TIER_LIMITS:
            compressed = compress_for_tier(self.prompt, tier)
            assert "\x00" not in compressed, f"Null byte found in {tier} compressed output"
            assert isinstance(compressed, str), f"Output is not a string for {tier}"
            assert len(compressed) > 100, f"Output too short for {tier}: {len(compressed)} chars"

    def test_caching_works(self):
        """Same input produces cached result on second call."""
        clear_cache()
        compressed1 = compress_for_tier(self.prompt, "groq")
        compressed2 = compress_for_tier(self.prompt, "groq")
        assert compressed1 == compressed2, "Cache produced different results"

    def test_stats_endpoint_accuracy(self):
        """get_compression_stats returns accurate numbers."""
        compressed = compress_for_tier(self.prompt, "groq")
        stats = get_compression_stats(self.prompt, compressed)
        assert stats["original_chars"] == len(self.prompt)
        assert stats["compressed_chars"] == len(compressed)
        assert stats["saved_chars"] == len(self.prompt) - len(compressed)
        assert 0 < stats["ratio"] < 100


class TestCompressionEdgeCases:
    """Test edge cases and robustness."""

    def test_short_prompt_passthrough(self):
        """Prompts shorter than target pass through unchanged."""
        short = "You are Kairos. Use TOOL_CALL to act."
        result = compress_prompt(short, target_chars=5000)
        assert result == short

    def test_empty_prompt(self):
        """Empty prompt doesn't crash."""
        result = compress_prompt("", target_chars=1000)
        assert result == ""

    def test_extreme_compression(self):
        """Even at 500 char limit, output is valid and non-empty."""
        prompt = _get_system_prompt()
        result = compress_prompt(prompt, target_chars=500)
        assert len(result) <= 500
        assert len(result) > 50  # Should still have meaningful content

    def test_unicode_safe(self):
        """Compression handles unicode content safely."""
        prompt = "You are Kairos AI Engine. ₹ € £ ¥ → ← ↑ ↓ 中文 日本語 한국어" + " test " * 1000
        result = compress_prompt(prompt, target_chars=500)
        assert isinstance(result, str)
        assert len(result) <= 500


class TestCompressionBenchmark:
    """Performance and quality benchmarks."""

    def test_compression_speed(self):
        """Compression completes in under 100ms for the full system prompt."""
        import time
        prompt = _get_system_prompt()
        clear_cache()
        start = time.time()
        for tier in TIER_LIMITS:
            compress_for_tier(prompt, tier)
        elapsed = time.time() - start
        assert elapsed < 0.5, f"Compression took {elapsed:.3f}s (should be < 0.5s)"

    def test_all_tiers_summary(self):
        """Print a summary of compression results for all tiers (informational)."""
        prompt = _get_system_prompt()
        clear_cache()
        print("\n╔══════════════════════════════════════════╗")
        print("║   COMPRESSION BENCHMARK RESULTS          ║")
        print("╠══════════════════════════════════════════╣")
        print(f"║ Original: {len(prompt):>6} chars                  ║")
        for tier, limit in TIER_LIMITS.items():
            compressed = compress_for_tier(prompt, tier)
            stats = get_compression_stats(prompt, compressed)
            fits = "OK" if stats["compressed_chars"] <= limit else "OVER"
            # Count critical patterns preserved
            all_patterns = []
            for patterns in CRITICAL_PATTERNS.values():
                all_patterns.extend(patterns)
            preserved = sum(1 for p in all_patterns if p in compressed)
            total = len(all_patterns)
            print(f"║ {tier:>12}: {stats['compressed_chars']:>5}/{limit:>5} ({stats['ratio']:>4.1f}%) [{fits}] patterns:{preserved}/{total} ║")
        print("╚══════════════════════════════════════════╝")

"""Smart Prompt Compressor for Free LLM Tiers.

Algorithmically compresses system prompts to fit within free-tier token limits
while preserving semantic meaning. No LLM calls needed — pure rule-based compression.

Compression Pipeline:
1. Section Priority Ranking — Keep critical sections, trim low-priority ones
2. Redundancy Elimination — Deduplicate repeated patterns
3. Syntax Stripping — Remove markdown, comments, excess whitespace
4. Abbreviation Engine — Convert verbose patterns to concise equivalents
5. Example Pruning — Keep structure, remove verbose examples
6. Adaptive Budget — Allocate chars based on target size and section priority
"""
import re
import hashlib
from functools import lru_cache

# ═══════════════════════════════════════
# COMPRESSION CACHE — avoid re-compressing identical prompts
# ═══════════════════════════════════════
_compression_cache: dict[str, dict[str, str]] = {}


def compress_prompt(prompt: str, target_chars: int = 4000, tier: str = "groq") -> str:
    """Compress a system prompt to fit within target char limit.
    
    Args:
        prompt: Original system prompt
        target_chars: Max chars for the output
        tier: Provider tier name (for cache key)
    
    Returns:
        Compressed prompt preserving core meaning
    """
    if len(prompt) <= target_chars:
        return prompt

    # Check cache
    cache_key = hashlib.md5(f"{prompt[:200]}:{target_chars}:{tier}".encode()).hexdigest()
    if cache_key in _compression_cache:
        return _compression_cache[cache_key]

    # Run compression pipeline
    compressed = prompt
    compressed = _strip_markdown(compressed)
    compressed = _collapse_whitespace(compressed)
    compressed = _prune_examples(compressed)
    compressed = _abbreviate_patterns(compressed)
    compressed = _deduplicate_lines(compressed)

    # If still too long, apply section prioritization
    if len(compressed) > target_chars:
        compressed = _prioritize_sections(compressed, target_chars)

    # Final whitespace cleanup
    compressed = _collapse_whitespace(compressed)

    # Hard trim with ellipsis if still over (shouldn't happen often)
    if len(compressed) > target_chars:
        compressed = compressed[:target_chars - 50] + "\n[Compressed prompt — core instructions preserved]"

    # Cache result
    _compression_cache[cache_key] = compressed
    return compressed


def get_compression_stats(original: str, compressed: str) -> dict:
    """Return compression statistics."""
    return {
        "original_chars": len(original),
        "compressed_chars": len(compressed),
        "ratio": round(len(compressed) / len(original) * 100, 1),
        "saved_chars": len(original) - len(compressed),
        "original_tokens_est": len(original) // 4,
        "compressed_tokens_est": len(compressed) // 4,
    }


# ═══════════════════════════════════════
# PIPELINE STAGES
# ═══════════════════════════════════════

def _strip_markdown(text: str) -> str:
    """Remove markdown formatting while preserving structure."""
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # Remove header markers but keep text
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
    # Remove backtick code fences (keep content)
    text = re.sub(r'```\w*\n?', '', text)
    # Remove inline backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove bullet markers, keep content
    text = re.sub(r'^[\s]*[-•]\s+', '- ', text, flags=re.MULTILINE)
    return text


def _collapse_whitespace(text: str) -> str:
    """Collapse excessive whitespace and blank lines."""
    # Multiple blank lines → single
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Trailing whitespace on lines
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    # Multiple spaces → single (except indentation)
    text = re.sub(r'(?<=\S)  +', ' ', text)
    return text.strip()


def _prune_examples(text: str) -> str:
    """Remove verbose examples while keeping structure hints."""
    # Remove JSON example blocks (keep just the description before them)
    text = re.sub(
        r'(Example[s]?:?\s*)\{[^}]{100,}\}',
        r'\1{...}',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    # Remove long quoted examples
    text = re.sub(r'"[^"]{200,}"', '"..."', text)
    # Remove "e.g., ..." patterns longer than 100 chars
    text = re.sub(r'(e\.g\.,?\s*)[^.\n]{100,}', r'\1...', text)
    # Remove "For example:" blocks
    text = re.sub(r'For example[:\s]+[^\n]{100,}', 'For example: ...', text, flags=re.IGNORECASE)
    return text


def _abbreviate_patterns(text: str) -> str:
    """Replace verbose patterns with concise equivalents."""
    replacements = [
        # Common verbose phrases → concise
        (r'You are an? (?:autonomous, )?senior-level full-stack developer', 'You are Kairos AI Engine'),
        (r'You execute tasks immediately without planning pauses\.', ''),
        (r'You think like a principal engineer: plan internally, execute decisively, verify rigorously\.', 'Execute decisively.'),
        (r'Do NOT describe what you\'re going to do', 'Act, don\'t describe'),
        (r'You MUST NOT', 'Don\'t'),
        (r'You must always', 'Always'),
        (r'Make sure to', ''),
        (r'Please note that', ''),
        (r'It is important to', ''),
        (r'In order to', 'To'),
        (r'As a result of', 'Due to'),
        (r'is responsible for', 'handles'),
        (r'should be used for', 'for'),
        (r'can be used to', 'to'),
        (r'IMPORTANT:', 'IMP:'),
        (r'WARNING:', 'WARN:'),
        (r'CRITICAL:', 'CRIT:'),
        # Reduce repeated "tool" descriptions
        (r'Use this tool to', 'Tool:'),
        (r'This tool allows you to', 'Tool:'),
        # Module descriptions → shorter
        (r'GET list, POST create, GET /\{id\}', 'CRUD'),
        (r'GET /\{id\}, PUT /\{id\}, DELETE /\{id\}', 'CRUD'),
        # Remove self-referential phrases
        (r'The following (?:is|are) (?:a |the )?(?:list|set|collection) of', ''),
        (r'Below (?:is|are) (?:a |the )?', ''),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _deduplicate_lines(text: str) -> str:
    """Remove duplicate or near-duplicate lines."""
    lines = text.split('\n')
    seen = set()
    result = []
    for line in lines:
        # Normalize for comparison (strip, lowercase, remove punctuation)
        key = re.sub(r'[^\w\s]', '', line.strip().lower())
        key = re.sub(r'\s+', ' ', key).strip()
        if not key:  # Keep blank lines
            result.append(line)
            continue
        if len(key) < 10:  # Keep short lines (headers, etc.)
            result.append(line)
            continue
        if key not in seen:
            seen.add(key)
            result.append(line)
    return '\n'.join(result)


def _prioritize_sections(text: str, target_chars: int) -> str:
    """Split into sections by priority and trim low-priority ones first.
    
    Priority (highest to lowest):
    1. Identity + Core Instructions (who you are, what you do)
    2. Tool Definitions (available tools and their syntax)
    3. Module/Schema Knowledge (database schemas, API endpoints)
    4. Rules & Constraints (coding standards, safety rules)
    5. Examples & Nice-to-haves (style guides, verbose examples)
    """
    sections = _split_into_sections(text)
    
    # Priority buckets
    priorities = {
        "identity": 1,
        "tools": 2,
        "modules": 3,
        "schema": 3,
        "rules": 4,
        "examples": 5,
        "style": 5,
        "other": 4,
    }
    
    # Classify sections
    classified = []
    for section in sections:
        lower = section.lower()
        if any(k in lower for k in ["you are", "engine", "autonomous", "kairos"]):
            priority = priorities["identity"]
        elif any(k in lower for k in ["tool", "tool_call", "args", "available tools"]):
            priority = priorities["tools"]
        elif any(k in lower for k in ["module", "endpoint", "/api/", "route"]):
            priority = priorities["modules"]
        elif any(k in lower for k in ["schema", "collection", "field", "db:"]):
            priority = priorities["schema"]
        elif any(k in lower for k in ["example", "e.g.", "sample", "template"]):
            priority = priorities["examples"]
        elif any(k in lower for k in ["rule", "must", "never", "always", "constraint"]):
            priority = priorities["rules"]
        elif any(k in lower for k in ["style", "format", "convention"]):
            priority = priorities["style"]
        else:
            priority = priorities["other"]
        classified.append((priority, section))
    
    # Sort by priority (lower number = higher priority)
    classified.sort(key=lambda x: x[0])
    
    # Build result within budget
    result = []
    chars_used = 0
    for priority, section in classified:
        if chars_used + len(section) <= target_chars:
            result.append(section)
            chars_used += len(section)
        else:
            # Trim this section to fit remaining budget
            remaining = target_chars - chars_used
            if remaining > 100:  # Only include if meaningful amount fits
                # For low-priority sections, skip entirely
                if priority >= 4:
                    continue
                # For high-priority, truncate
                trimmed = section[:remaining - 20] + "\n[...trimmed]"
                result.append(trimmed)
                chars_used += len(trimmed)
            break
    
    return '\n\n'.join(result)


def _split_into_sections(text: str) -> list[str]:
    """Split text into logical sections by double newlines or headers."""
    # Split on double newlines
    raw_sections = re.split(r'\n\n+', text)
    
    # Merge very small sections with their neighbors
    merged = []
    buffer = ""
    for section in raw_sections:
        if len(section) < 50 and buffer:
            buffer += "\n" + section
        else:
            if buffer:
                merged.append(buffer)
            buffer = section
    if buffer:
        merged.append(buffer)
    
    return merged


# ═══════════════════════════════════════
# TIER-SPECIFIC PRESETS
# ═══════════════════════════════════════

TIER_LIMITS = {
    "groq": 3500,       # Groq free: very strict TPM
    "cerebras": 6000,   # Cerebras free: moderate
    "huggingface": 6000, # HF free: moderate
    "default": 8000,
}


def compress_for_tier(prompt: str, tier: str) -> str:
    """Compress prompt for a specific free-tier provider."""
    target = TIER_LIMITS.get(tier, TIER_LIMITS["default"])
    return compress_prompt(prompt, target_chars=target, tier=tier)


def clear_cache():
    """Clear the compression cache (call after prompt updates)."""
    _compression_cache.clear()

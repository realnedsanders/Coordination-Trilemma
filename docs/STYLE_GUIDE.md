# Writing Style Guide

## Purpose

This document establishes writing standards for the Coordination Trilemma paper. The guide ensures consistency, mathematical rigor, and a natural human voice while avoiding markers of low-effort/anti-intellectual/unacademic content.

## Core Principles

### Voice and Tone

The paper adopts an **authoritative but accessible** voice that:

- Presents complex mathematical arguments with clarity
- Maintains intellectual humility about uncertainties
- Engages the reader as a thoughtful interlocutor
- Avoids both excessive formality and casual informality

### The Human Responsibility Principle

**AI should be used as a tool for thought decompression, not thought replacement.**

Every sentence in this document represents a human author taking responsibility for its consequences. AI assistance may help:
- Expand compressed ideas into fuller exposition
- Identify logical gaps or inconsistencies
- Suggest alternative phrasings
- Check mathematical notation consistency

But the human author must:
- Understand every claim being made
- Verify every mathematical statement
- Take responsibility for every argument
- Approve every word as their own

If you cannot defend a sentence in conversation, do not include it.

---

## Anti-Patterns to Avoid

### 1. Ordinal Enumeration Patterns

**Avoid:**
```
First, we establish X. Second, we prove Y. Third, we show Z. Finally, we conclude W.
```

**Prefer:**
```
The argument proceeds through establishing X, which enables the proof of Y. This in turn demonstrates Z, leading to the conclusion W.
```

Or use logical connectives that reflect actual relationships:
```
We establish X. Because X holds, Y follows. The combination of X and Y implies Z, from which W is immediate.
```

### 2. Excessive Transitional Phrases

**Avoid overuse of:**
- "Moreover" / "Furthermore" / "Additionally"
- "It is important to note that"
- "It should be emphasized that"
- "Interestingly"

**Prefer:** Let the logical structure carry the argument. If a point truly follows from the previous one, the connection should be apparent without verbal scaffolding.

### 3. Outline-Style Formatting in Prose Sections

**Avoid:**
```
**Setup:** The system begins with...
**Core insight:** The key observation is...
**Implication:** This means that...
```

**Prefer:** Flowing prose that integrates these elements:
```
The system begins with [setup], and the key observation is [insight]. This implies [implication].
```

### 4. Hedging Clusters

**Avoid:**
```
It could potentially be argued that this might possibly suggest...
```

**Prefer:** State claims at appropriate confidence levels:
```
This suggests... [medium confidence]
This establishes... [high confidence]
We conjecture that... [low confidence]
```

### 5. Performative Metacommentary

**Avoid:**
```
Let us now turn our attention to...
We shall proceed to examine...
It remains to be shown that...
```

**Prefer:** Simply make the turn:
```
[New topic sentence that introduces the next point]
```

### 6. Redundant Emphasis

**Avoid:**
```
This is extremely important and critical to understand.
The key essential point here is fundamentally that...
```

**Prefer:** State once with appropriate emphasis:
```
This is critical: [statement].
```

### 7. List-Heavy Exposition

**Avoid:** Multiple consecutive itemize/enumerate environments in argumentative sections.

**Prefer:** Reserve lists for:
- Genuinely parallel items (assumptions, conditions)
- Reference materials (theorem lists, citations)
- Tabular data

Convert argumentative lists to flowing prose.

### 8. Passive Voice Overuse

**Avoid:**
```
It was shown that X. It can be seen that Y. It is concluded that Z.
```

**Prefer:**
```
We showed X. Y follows from this. Therefore Z.
```

Or when the agent is genuinely irrelevant:
```
X holds. Y is immediate. Z follows.
```

### 9. Filler Phrases

**Avoid:**
- "In order to" (use "to")
- "Due to the fact that" (use "because")
- "At this point in time" (use "now")
- "In the event that" (use "if")
- "With regard to" (use "about" or "regarding")

### 10. Repetitive Sentence Structure

**Avoid:** Multiple consecutive sentences with identical structure:
```
The system requires X. The system demands Y. The system needs Z.
```

**Prefer:** Vary structure while maintaining clarity:
```
The system requires X and demands Y. It also needs Z to function properly.
```

---

## Mathematical Writing Standards

### Notation Consistency

- Define all symbols at first use
- Use consistent notation throughout (e.g., always $\theta$ for proportion, never switching to $p$)
- Reference the Glossary for standard notation
- Prefer semantic notation: $\theta_{\text{crit}}$ over $\theta^*$ when meaning matters

### Theorem Statements

- State theorems in complete, self-contained form
- Include all assumptions explicitly
- Number theorems by section for navigability (e.g., Theorem 3.2)
- Provide intuition before formal statement when helpful

### Proof Style

- Begin with proof strategy when non-obvious
- Use "we show" rather than "it will be shown"
- Mark proof end clearly ($\square$ for lemmas, $\blacksquare$ for main theorems)
- Break long proofs into labeled parts

### Inline Mathematics

- Use inline math for simple expressions: $n > 10^7$
- Use display math for:
  - Equations referenced later
  - Complex expressions
  - Key results deserving emphasis

### Conditional Statements

**Prefer:**
```
If X, then Y.
```

**Over:**
```
Given that X is the case, it follows that Y must hold.
```

---

## Confidence Calibration

### Explicit Uncertainty

State confidence levels for empirical claims:

- **Very High (>90%):** Use definitive language ("establishes," "proves," "demonstrates")
- **High (>80%):** Use confident language ("shows," "indicates," "confirms")
- **Medium (50-80%):** Use measured language ("suggests," "supports," "is consistent with")
- **Low (<50%):** Use tentative language ("may," "could," "is possible that")

### Falsification Criteria

For major claims, state what evidence would falsify them. This demonstrates intellectual honesty and scientific rigor.

---

## Document-Specific Conventions

### Section Headings

- Use `\subsection{}` for major divisions within appendices
- Use `\heading{}` for lightweight topical breaks (defined in main.tex)
- Avoid subsection headers in Table of Contents for reference material (Glossary)

### Cross-References

- Use `\ref{}` for numbered items (theorems, sections, figures)
- Use `\hyperref[]{}` for named destinations (Glossary)
- Ensure all referenced labels exist

### Citations

- Cite peer-reviewed sources when available
- Note confidence level for non-peer-reviewed sources
- Prefer recent comprehensive sources over multiple older partial ones

---

## AI Collaboration Guidelines

### Appropriate Uses

1. **Thought decompression:** Expanding bullet points into prose
2. **Consistency checking:** Finding notation inconsistencies
3. **Pattern detection:** Identifying anti-patterns in existing text
4. **Alternative phrasings:** Suggesting clearer ways to express ideas
5. **Structural analysis:** Evaluating logical flow

### Inappropriate Uses

1. **Writing without understanding:** Never include text you cannot fully explain
2. **Avoiding responsibility:** The human author owns every word
3. **Replacing judgment:** AI cannot assess truth or importance

### The Approval Gate

Before accepting any AI-suggested text:

1. **Understand it:** Can you explain every claim to a colleague?
2. **Verify it:** Have you checked factual and mathematical claims?
3. **Own it:** Are you willing to defend it in peer review?
4. **Need it:** Does it actually improve the document?

If any answer is "no," revise or reject the suggestion.

### Disclosure

This document was developed with AI assistance for thought decompression and editing. All arguments, claims, and final text represent the human author's considered judgment and responsibility.

---

## Automated Quality Checks

### Recommended Tools

The following tools can be integrated into GitHub Actions for automated prose analysis:

#### 1. write-good
- **Purpose:** Identifies passive voice, weasel words, and other weak constructions
- **Installation:** `npm install write-good`
- **Configuration:** Create `.write-good.json` to customize rules

#### 2. textlint
- **Purpose:** Pluggable linting for natural language
- **Installation:** `npm install textlint`
- **Useful plugins:**
  - `textlint-rule-no-start-duplicated-conjunction`
  - `textlint-rule-no-dead-link`
  - `textlint-rule-terminology`

#### 3. proselint
- **Purpose:** Checks for common prose errors
- **Installation:** `pip install proselint`
- **Checks:** Jargon, redundancy, inconsistency

#### 4. alex
- **Purpose:** Catches insensitive or inconsiderate writing
- **Installation:** `npm install alex`

#### 5. LaTeX-specific: ChkTeX
- **Purpose:** LaTeX semantic checker
- **Installation:** Usually bundled with TeX distributions
- **Checks:** Common LaTeX mistakes and style issues

### GitHub Actions Integration

See `.github/workflows/prose-lint.yml` for implementation (to be created).

### Custom Checks

Consider implementing custom checks for:

1. **Ordinal pattern detection:** Regex for "First...Second...Third...Finally"
2. **List density:** Warning when >3 consecutive itemize environments
3. **Transition word frequency:** Alert on overuse of specific transitions
4. **Sentence length variance:** Flag sections with low variance (repetitive structure)
5. **Passive voice ratio:** Target <20% passive constructions

---

## Review Checklist

Before finalizing any section, verify:

### Content
- [ ] All claims are accurate and defensible
- [ ] Mathematical statements are correct
- [ ] Confidence levels are appropriate
- [ ] Falsification criteria provided for major claims

### Style
- [ ] No ordinal enumeration patterns
- [ ] Minimal transitional phrase scaffolding
- [ ] Lists converted to prose where appropriate
- [ ] Sentence structure varies
- [ ] Passive voice used only when appropriate

### Technical
- [ ] All notation defined and consistent
- [ ] All cross-references resolve
- [ ] Citations are appropriate confidence level
- [ ] LaTeX compiles without warnings

### AI Collaboration
- [ ] All text is understood by human author
- [ ] All claims verified by human author
- [ ] Human author takes full responsibility
- [ ] Disclosure is appropriate

---

## Version History

- **v1.0 (2025-11-17):** Initial style guide based on editing sessions

## Contributing

Propose additions or modifications to this guide through pull requests. Include rationale for suggested changes and examples demonstrating the issue and solution.

#!/bin/bash
# Prose quality checker for Coordination Trilemma paper
# Checks for known anti-patterns defined in docs/STYLE_GUIDE.md

set -e

TEX_DIR="src/tex"
ISSUES_FOUND=0

echo "=== Custom Prose Anti-Pattern Analysis ==="
echo ""

# Colors for output (if terminal supports it)
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

warn() {
    echo -e "${YELLOW}WARNING:${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

info() {
    echo -e "${GREEN}INFO:${NC} $1"
}

error() {
    echo -e "${RED}ERROR:${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

# 1. Check for ordinal enumeration patterns
echo "--- Checking for ordinal enumeration patterns ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # Pattern: First...Second...Third or First...Then...Next...Finally
        if grep -n -i "First,.*Second,.*Third" "$file" 2>/dev/null; then
            warn "$file: Found 'First, Second, Third' pattern"
        fi
        if grep -n -i "First.*\. Then.*\. Next.*\. Finally" "$file" 2>/dev/null; then
            warn "$file: Found 'First...Then...Next...Finally' pattern"
        fi
        # Also check for numbered prose (not in enumerate)
        if grep -n "^[[:space:]]*1\.[[:space:]].*2\.[[:space:]].*3\." "$file" 2>/dev/null; then
            warn "$file: Found inline numbered list in prose"
        fi
    fi
done
echo ""

# 2. Check for excessive transitional phrases
echo "--- Checking for overused transitional phrases ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # Count occurrences of common overused transitions
        moreover_count=$(grep -c -i "Moreover" "$file" 2>/dev/null || echo 0)
        furthermore_count=$(grep -c -i "Furthermore" "$file" 2>/dev/null || echo 0)
        additionally_count=$(grep -c -i "Additionally" "$file" 2>/dev/null || echo 0)

        total=$((moreover_count + furthermore_count + additionally_count))
        if [ "$total" -gt 10 ]; then
            warn "$file: High transitional phrase count ($total instances of Moreover/Furthermore/Additionally)"
        fi

        # Check for "It is important to note"
        important_note=$(grep -c -i "It is important to note\|It should be noted\|It should be emphasized" "$file" 2>/dev/null || echo 0)
        if [ "$important_note" -gt 3 ]; then
            warn "$file: Overuse of 'It is important to note' pattern ($important_note instances)"
        fi
    fi
done
echo ""

# 3. Check for list density (consecutive itemize/enumerate)
echo "--- Checking for excessive list density ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # This is a simplified check - looks for patterns suggesting dense lists
        # Count begin{itemize} and begin{enumerate}
        list_count=$(grep -c "\\\\begin{itemize}\|\\\\begin{enumerate}" "$file" 2>/dev/null || echo 0)
        line_count=$(wc -l < "$file")

        # If more than 1 list per 20 lines, flag it
        if [ "$line_count" -gt 0 ]; then
            ratio=$((list_count * 20 / line_count))
            if [ "$ratio" -gt 1 ] && [ "$list_count" -gt 5 ]; then
                warn "$file: High list density ($list_count lists in $line_count lines)"
            fi
        fi
    fi
done
echo ""

# 4. Check for outline-style formatting in prose sections
echo "--- Checking for outline-style formatting ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # Look for bold labels followed by colons (outline style)
        outline_count=$(grep -c "\\\\textbf{[^}]*}:" "$file" 2>/dev/null || echo 0)
        if [ "$outline_count" -gt 15 ]; then
            warn "$file: Many outline-style bold labels ($outline_count instances of '\\textbf{...}:')"
        fi
    fi
done
echo ""

# 5. Check for hedging clusters
echo "--- Checking for hedging clusters ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # Look for multiple hedging words in proximity
        if grep -n -i "could potentially\|might possibly\|may perhaps\|possibly could" "$file" 2>/dev/null; then
            warn "$file: Found hedging cluster"
        fi
    fi
done
echo ""

# 6. Check for filler phrases
echo "--- Checking for filler phrases ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        filler_count=0

        # "In order to" -> "to"
        in_order_to=$(grep -c -i "in order to" "$file" 2>/dev/null || echo 0)
        filler_count=$((filler_count + in_order_to))

        # "Due to the fact that" -> "because"
        due_to_fact=$(grep -c -i "due to the fact that" "$file" 2>/dev/null || echo 0)
        filler_count=$((filler_count + due_to_fact))

        # "At this point in time" -> "now"
        at_this_point=$(grep -c -i "at this point in time" "$file" 2>/dev/null || echo 0)
        filler_count=$((filler_count + at_this_point))

        if [ "$filler_count" -gt 3 ]; then
            warn "$file: Found $filler_count filler phrases (in order to, due to the fact that, etc.)"
        fi
    fi
done
echo ""

# 7. Check for performative metacommentary
echo "--- Checking for performative metacommentary ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        meta_count=$(grep -c -i "Let us now turn\|We shall proceed\|It remains to be shown\|We will now examine" "$file" 2>/dev/null || echo 0)
        if [ "$meta_count" -gt 3 ]; then
            warn "$file: Found $meta_count instances of performative metacommentary"
        fi
    fi
done
echo ""

# 8. Check passive voice indicators (basic check)
echo "--- Checking for passive voice indicators ---"
for file in "$TEX_DIR"/*.tex "$TEX_DIR"/appendices/*.tex; do
    if [ -f "$file" ]; then
        # Simple heuristic: "was/were/is/are + past participle" patterns
        passive_count=$(grep -c -i "was shown\|were found\|is concluded\|are determined\|was established\|were observed" "$file" 2>/dev/null || echo 0)
        if [ "$passive_count" -gt 10 ]; then
            warn "$file: High passive voice indicator count ($passive_count instances)"
        fi
    fi
done
echo ""

# Summary
echo "=========================================="
if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo -e "${GREEN}No major anti-patterns detected.${NC}"
else
    echo -e "${YELLOW}Found $ISSUES_FOUND potential issues.${NC}"
    echo "Review warnings above and consult docs/STYLE_GUIDE.md"
fi
echo "=========================================="

# Exit with warning status if issues found (but don't fail the build)
exit 0

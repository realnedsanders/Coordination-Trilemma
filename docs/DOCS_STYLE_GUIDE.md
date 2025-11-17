# Documentation Style Guide

**Last Updated:** 2025-11-17
**Audience:** Contributors, Maintainers

This guide establishes standards for documentation in the Coordination Trilemma project to ensure
consistency, clarity, and maintainability.

## Document Structure

### Required Elements

Every documentation file should include:

```markdown
# Document Title

**Last Updated:** YYYY-MM-DD
**Audience:** Who this doc is for (e.g., "Builders", "Contributors", "Security Researchers")
**Status:** (optional) For planning docs (e.g., "Completed", "In Progress", "Deprecated")

Brief description of what this document covers (1-2 sentences).

**See also:**
- [Related Doc 1](path.md) - Brief description
- [Related Doc 2](path.md) - Brief description

## First Section...
```

### Metadata Fields

**Last Updated:** Always use YYYY-MM-DD format (ISO 8601)

- Update whenever making significant changes
- Minor typo fixes don't require date updates

**Audience:** Choose from:

- **All Users** - Everyone
- **New Users** - First-time builders
- **Builders** - People compiling the PDF
- **Developers** - People modifying code
- **Contributors** - People submitting PRs
- **Maintainers** - Project maintainers
- **Security Researchers** - Security auditors/verifiers
- **Advanced Users** - Power users

**Status:** (Optional) Use for planning/roadmap docs:

- `Completed` - Done
- `In Progress` - Actively working on
- `Planning` - Future work
- `Deprecated` - Obsolete, kept for reference

### "See also" Section

Include 2-5 related documents with brief descriptions:

```markdown
**See also:**
- [BUILD.md](BUILD.md) - Complete build instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
```

## Writing Style

### Tone

- **Clear and direct** - Get to the point quickly
- **Helpful, not condescending** - Assume intelligence, explain complexity
- **Professional but approachable** - Academic project, but readable
- **Action-oriented** - Focus on what to do, not just what is

### Voice

- **Active voice preferred** - "Run the command" not "The command should be run"
- **Second person for instructions** - "You should..." or imperative "Run..."
- **First person plural for the project** - "We use Alpine Linux"

### Formatting

#### Headers

- **H1 (`#`)** - Document title only (one per file)
- **H2 (`##`)** - Main sections
- **H3 (`###`)** - Subsections
- **H4 (`####`)** - Rarely needed, use sparingly

**Examples:**

```markdown
# Document Title
## Main Section
### Subsection
```

#### Lists

- Use `-` for unordered lists (not `*` or `+`)
- Use `1.` for ordered lists (automatic numbering)
- Indent sub-items with 2 spaces

**Example:**

```markdown
- First item
  - Sub-item
  - Another sub-item
- Second item

1. First step
2. Second step
3. Third step
```

#### Code Blocks

- Always specify language for syntax highlighting
- Use descriptive labels for terminal sessions

**Examples:**

```markdown
​```bash
make clean
make
​```

​```yaml
# GitHub Actions
on: push
​```

​```latex
\section{Example}
​```
```

#### Inline Code

- Use backticks for `commands`, `file names`, `variables`
- Use for exact strings user will type or see

#### Emphasis

- **Bold** for important terms, warnings, emphasis
- *Italic* sparingly for softer emphasis
- Don't use CAPS for emphasis (except acronyms)

#### Links

- Use relative links for internal docs: `[BUILD.md](BUILD.md)`
- Use descriptive text: `[build instructions](BUILD.md)` not `[click here](BUILD.md)`
- External links: `[Docker Docs](https://docs.docker.com/)`

## Code Examples

### Shell Commands

**Show from repository root:**

```markdown
​```bash
# Always assume user is at repository root
make clean
./scripts/verify-signatures.sh
```

**Not:**

```bash
# Don't show from subdirectories unless necessary
cd scripts && ./verify-signatures.sh
```

**Include comments for clarity:**

```bash
# Download Docker image (one-time, ~500MB)
make docker-pull

# Build PDF
make
```

**Show expected output when helpful:**

```bash
$ make
Compiling PDF...
✓ PDF generated: main.pdf
```

### Multi-step Procedures

Use numbered lists with code blocks:

```markdown
1. Install Docker:
   ​```bash
   brew install --cask docker
   ​```

2. Build the PDF:
   ​```bash
   make docker-pull
   make
   ​```

3. Verify the output:
   ​```bash
   ls -lh main.pdf
   ​```
```

### Command Options

Show full commands with explanations:

```markdown
​```bash
docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir/src/tex \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest \
  pdflatex main
​```

**Flags explained:**
- `--rm` - Remove container after run
- `-v $(pwd):/workdir` - Mount current directory
- `-w /workdir/src/tex` - Set working directory
```

## Special Elements

### Callouts

Use emoji and bold for different types of callouts:

```markdown
**✅ Success:** Command completed successfully

**⚠️ Warning:** This will delete all files

**❌ Error:** Build failed

**💡 Tip:** Use `make help` to see all commands

**📝 Note:** Output goes to main.pdf
```

### Tables

Use tables for comparisons, reference info, or structured data:

```markdown
| Command | Purpose | Example |
|---------|---------|---------|
| `make` | Build PDF | `make` |
| `make view` | Open PDF | `make view` |
| `make clean` | Clean files | `make clean` |
```

**Align:**

- Left-align text columns
- Center-align short content
- Right-align numbers

### Decision Trees

Use Markdown to show decision flows:

```markdown
**Which Docker image should I use?**

- Need all LaTeX packages? → `texlive/texlive:latest` (~4-5GB)
- Building this project only? → `ghcr.io/.../latex:latest` (~500MB-1GB)
- Signing artifacts? → `ghcr.io/.../security:latest` (~50-100MB)
```

### Visual Diagrams

**Use Mermaid for diagrams** - GitHub renders Mermaid natively:

#### Flowcharts

```markdown
​```mermaid
flowchart TD
    A[User runs make] --> B[Makefile]
    B --> C[Docker]
    C --> D[LaTeX]
    D --> E[PDF Output]

    style A fill:#e1f5ff
    style E fill:#e1ffe1
​```
```

#### Sequence Diagrams

```markdown
​```mermaid
sequenceDiagram
    participant User
    participant Make
    participant Docker
    participant LaTeX

    User->>Make: make
    Make->>Docker: docker run
    Docker->>LaTeX: pdflatex
    LaTeX-->>Docker: main.pdf
    Docker-->>Make: PDF ready
    Make-->>User: Build complete
​```
```

#### State Diagrams

```markdown
​```mermaid
stateDiagram-v2
    [*] --> Clean
    Clean --> Building: make
    Building --> Built: success
    Building --> Failed: error
    Built --> Clean: make clean
    Failed --> Clean: make clean
​```
```

#### Git Graphs

```markdown
​```mermaid
gitGraph
    commit
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
​```
```

**Mermaid Styling Tips:**

- Use colors: `style A fill:#e1f5ff` (light blue for triggers)
- Use colors: `style B fill:#fff4e1` (light yellow for processing)
- Use colors: `style C fill:#ffe1e1` (light red for critical steps)
- Use colors: `style D fill:#e1ffe1` (light green for success/output)
- Keep node text concise, use `<br/>` for line breaks
- Add subgraphs for logical grouping

**ASCII Art Fallback:**
Only use ASCII if Mermaid doesn't support the diagram type:

```markdown
​```
Simple: A → B → C
​```
```

## File Naming

### Documentation Files

- **UPPERCASE.md** - Top-level important docs (README, LICENSE, CONTRIBUTING, CHANGELOG)
- **lowercase-with-dashes.md** - Regular docs (quick start-guide.md)
- **PascalCase.md** - Planning/roadmap docs (SLSA_ROADMAP.md)

### Sections

- Use kebab-case for anchor links: `#build-instructions`
- No spaces, lowercase only

## Content Guidelines

### Be Comprehensive But Concise

- Cover the topic thoroughly
- Don't repeat information available elsewhere (link instead)
- Front-load important information

### Examples Over Explanation

- Show concrete examples
- Provide copy-pasteable commands
- Include expected output

### Troubleshooting Sections

- Start with most common issues
- Provide specific error messages where possible
- Always give a solution or next step

### Keep It Current

- Update "Last Updated" dates
- Remove obsolete information
- Mark deprecated features clearly

## Common Patterns

### Quick Start Sections

```markdown
## Quick Start

​```bash
# 1. Install dependencies
brew install docker

# 2. Build
make docker-pull
make

# Done! Your PDF is at main.pdf
​```
```

### Prerequisites

```markdown
## Prerequisites

**Required:**
- Docker 20.0+
- Git 2.0+

**Optional:**
- Local LaTeX (for `make local`)
```

### Troubleshooting

```markdown
### Error Message

**Cause:** Why this happens

**Solution:**
​```bash
# Commands to fix it
make clean && make
​```

**Verify:**
​```bash
# How to check it worked
ls -lh main.pdf
​```
```

## Documentation Types

### Tutorial (e.g., quickstart.md)

- Numbered steps
- Copy-pasteable commands
- Expected outcomes shown
- "What you get" section

### Reference (e.g., BUILD.md)

- Complete information
- Organized by topic
- Cross-referenced
- Examples for each feature

### Guide (e.g., CI-CD.md)

- Explain concepts
- Show relationships
- Diagrams helpful
- "How it works" focus

### Troubleshooting (e.g., TROUBLESHOOTING.md)

- Problem → Solution format
- Grouped by type
- Quick reference table
- "If all else fails" section

## Automated Linting

This project uses **markdownlint** to enforce documentation standards automatically.

### Configuration

Linting rules are defined in `.markdownlint.yaml` at the repository root:

**Key rules:**

- **Line length**: 120 characters (reasonable for documentation)
- **Heading style**: ATX-style (`#` not underlined)
- **List markers**: Use `-` for unordered lists
- **Code blocks**: Must specify language (` ```bash` not ` ``` `)
- **Proper names**: Correct capitalization (GitHub, Docker, LaTeX, SLSA)
- **HTML**: Allowed elements like `<br>`, `<img>`, `<table>` for badges and formatting

### Running Locally

Test your Markdown before committing:

```bash
# Using Docker (recommended)
docker run --rm -v "$(pwd)":/workdir \
  ghcr.io/igorshubovych/markdownlint-cli:latest \
  --config .markdownlint.yaml \
  docs/*.md

# Or install markdownlint-cli globally
npm install -g markdownlint-cli
markdownlint --config .markdownlint.yaml docs/*.md
```

### Common Issues

**Line too long:**

```markdown
# Bad
This is a very long line that exceeds the 120 character limit and will trigger a markdownlint warning about line length.

# Good
This is a very long line that exceeds the 120 character limit and will trigger
a markdownlint warning about line length.
```

**Missing code block language:**

```markdown
# Bad
​```
make
​```

# Good
​```bash
make
​```
```

**Inconsistent list markers:**

```markdown
# Bad
* Item 1
- Item 2

# Good
- Item 1
- Item 2
```

### CI Integration

Markdownlint runs automatically on:

- Every push to main
- Every pull request
- Weekly schedule

Failed linting will block PRs until fixed.

## Review Checklist

Before committing documentation:

- [ ] Metadata present (Last Updated, Audience)
- [ ] "See also" links included
- [ ] Code blocks have language specified
- [ ] Commands shown from repository root
- [ ] Links work (internal and external)
- [ ] No typos or grammar errors
- [ ] Examples are copy-pasteable
- [ ] Consistent with this style guide
- [ ] Renders correctly in GitHub
- [ ] **Passes markdownlint** (`markdownlint --config .markdownlint.yaml <file>.md`)

## Maintenance

### When to Update Docs

**Always update when:**

- Changing functionality
- Adding features
- Fixing bugs that affect usage
- Reorganizing files
- Changing workflows

**Update "Last Updated" when:**

- Significant content changes
- Restructuring
- Adding new sections

**Don't update "Last Updated" for:**

- Typo fixes
- Minor wording changes
- Formatting improvements

### Documentation Debt

If you can't update docs immediately:

1. Add `<!-- TODO: Update after X -->` comment
2. Create issue with `[docs]` tag
3. Link to issue in commit message

## Questions?

- **Style not covered here?** Check existing docs for precedent
- **Unsure about something?** Open an issue with `[docs]` tag
- **Want to improve this guide?** PRs welcome!

---

**This guide itself follows its own recommendations. Use it as a reference!**

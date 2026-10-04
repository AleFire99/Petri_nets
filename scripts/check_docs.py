"""Documentation coherence checks (run in CI): `uv run python scripts/check_docs.py`.

- relative Markdown links resolve to existing files
- every doc in docs/<topic>/ is linked from that folder's README.md
- code fences are balanced and mermaid blocks are non-empty
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def check_links(md: Path) -> list[str]:
    errors = []
    text = re.sub(r"```.*?```", "", md.read_text(), flags=re.DOTALL)
    for target in LINK.findall(text):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        path = target.split("#")[0]
        if path and not (md.parent / path).exists():
            errors.append(f"{md.relative_to(ROOT)}: broken link {target!r}")
    return errors


def check_fences(md: Path) -> list[str]:
    errors = []
    lines = md.read_text().splitlines()
    fences = [i for i, line in enumerate(lines) if line.startswith("```")]
    if len(fences) % 2:
        errors.append(f"{md.relative_to(ROOT)}: unbalanced code fences")
        return errors
    for start, end in zip(fences[::2], fences[1::2], strict=True):
        if (
            lines[start].strip() == "```mermaid"
            and not "".join(lines[start + 1 : end]).strip()
        ):
            errors.append(f"{md.relative_to(ROOT)}:{start + 1}: empty mermaid block")
    return errors


def check_indexes() -> list[str]:
    errors = []
    for topic in sorted(p for p in (ROOT / "docs").iterdir() if p.is_dir()):
        readme = topic / "README.md"
        if not readme.exists():
            errors.append(f"{topic.relative_to(ROOT)}: missing README.md index")
            continue
        index = readme.read_text()
        for doc in sorted(topic.glob("*.md")):
            if doc.name != "README.md" and doc.name not in index:
                errors.append(
                    f"{doc.relative_to(ROOT)}: not linked from {readme.relative_to(ROOT)}"
                )
    return errors


def main() -> int:
    docs = [
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
        *sorted((ROOT / "docs").rglob("*.md")),
    ]
    errors = check_indexes()
    for md in docs:
        errors += check_links(md) + check_fences(md)
    for e in errors:
        print(e)
    print(f"checked {len(docs)} markdown files: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

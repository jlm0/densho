import sys
from pathlib import Path

from knowledge_architecture.parser.node import parse_tree

USAGE_ERROR = 2


def main(arguments: list[str]) -> int:
    if not arguments:
        sys.stderr.write("Usage: python -m knowledge_architecture.parser <folder> [<folder> ...]\n")
        return USAGE_ERROR
    nodes, problems = parse_tree(Path(argument) for argument in arguments)
    for problem in problems:
        sys.stdout.write(f"{problem}\n")
    sys.stdout.write(f"{len(nodes)} nodes parsed, {len(problems)} problems\n")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

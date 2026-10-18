"""Resolve recorded diagram source paths without changing original manifests/hashes."""
from pathlib import Path
import json


def resolve_asset(repo, recorded_path):
    repo = Path(repo).resolve()
    source = repo / recorded_path
    if source.exists():
        return source
    mappings = json.loads((repo / 'docs_codex/diagrams/path_migrations.json').read_text())['directories']
    for old, new in mappings.items():
        origin = repo / old
        if source.is_relative_to(origin):
            target = repo / new / source.relative_to(origin)
            if target.exists():
                return target
    raise FileNotFoundError(f'No current or mapped diagram source: {recorded_path}')

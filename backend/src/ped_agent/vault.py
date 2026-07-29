from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ContentVault:
    def __init__(self, root: Path) -> None:
        self.root = root

    def put(self, source: Path, expected_sha256: str) -> Path:
        actual = sha256_file(source)
        if actual != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {source}")
        suffix = source.suffix.lower() or ".bin"
        target = self.root / actual[:2] / f"{actual}{suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        return target

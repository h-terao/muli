from pathlib import Path


class Command:
    @staticmethod
    def process():
        raise NotImplementedError

    def glob(self, in_dir: Path, ext: str = None):
        """

        In default, recursively search files.

        """
        if ext is None:
            ext = ""
        return Path(in_dir).rglob(f"*{ext}")

    @staticmethod
    def filter(x) -> bool:
        return True

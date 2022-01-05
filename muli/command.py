from pathlib import Path
import multiprocessing as mp
from functools import partial

from tqdm import tqdm


class Command:
    def __init__(self, n_jobs: int = -1):
        self._n_jobs = n_jobs

    def preprocess(self):
        pass

    def glob(self, in_dir: Path, ext: str = None):
        """

        In default, recursively search files.

        """
        if ext is None:
            ext = ""
        return Path(in_dir).rglob(f"*{ext}")

    def filter(self, x) -> bool:
        return True

    @staticmethod
    def step(x):
        raise NotImplementedError

    def after_step(self, result):
        return result

    def postprocess(self, results):
        pass

    def run(self, args):

        iterable = [
            x for x in self.glob(**args.get("glob", args))
            if self.filter(x, **args.get("filter", args))
        ]

        step = partial(self.step, **args.get("step", args))

        results = []
        if self.n_jobs == 0:
            with tqdm(iterable) as pbar:
                for input in pbar:
                    result = step(input)
                    result = self.after_step(result, **args.get("after_step", args))
                    results.append(result)
        else:
            with mp.Pool(self.n_jobs) as pool, tqdm(total=len(iterable)) as pbar:
                for result in pool.imap_unordered(step, iterable):
                    result = self.after_step(result, **args.get("after_step", args))
                    results.append(result)
                    pbar.update(1)

        self.postprocess(results, **args.get("postprocess", args))

    @property
    def n_jobs(self) -> int:
        if self._n_jobs is None:
            return 0
        elif self._n_jobs < 0:
            return max(0, mp.cpu_count() + 1 + self._n_jobs)
        else:
            return self._n_jobs

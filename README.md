# Multiprocessing CLI (muli)
Easy to implement simple CLI tools with multiprocessing and progressbar.
This project is now in progress.

## Requirements
- python3
- tqdm
- docstring_parser

## Install
```bash
pip install git+https://github.com/h-terao/muli
```

## Usage

### Add new subcommands

To add new subcommands, implement command class that inherits `muli.Command`.
The following example adds `new` subcommand and you can call by `python run.py new ...`.

```python
from muli import parser, Command

@parser.register()
class new(Command):
    def __init__(self, n_jobs: int):
        super().__init__(n_jobs)
    
    def preprocess(self):
        pass 
    
    def glob(self, in_dir: Path, ext: str):
        return in_dir.rglob(f"*{ext}")
    
    def filter(self, x):
        return True
    
    @staticmethod
    def step(x):
        # This process works in parallel.
        print(x)
    
    def after_step(self, result):
        return result
    
    def postprocess(self, results):
        pass 
```

You can omit methods but `step` in above example. 
These methods will work as like:

```python
cmd = new(n_jobs)
cmd.preprocess()

results = []
for item in glob(in_dir, ext):
    if not filter(item):
        continue

    result = cmd.step(item)
    result = cmd.after_step(result)
    results.append(result)

cmd.postprocess(results)
```

Note that the order of output results will not match with input order.

### Add options

You can add any options by adding parameters in Command's methods.
For example, if you implement a `filter` method that accepts a threshold parameter, threshold is automatically added into options of the subcommand.
In addition, you can set default values by set default values of methods' parameters.
Note that you must annotate types of parameters to decide types of parameters.

```python
def filter(self, x, threshold: float)  # threshold is required.

def filter(self, x, threshold: float = 0.5)  # threshold is optional.
```

Furthermore, you can register short names and help messages of options via docstrings.
For example, the following docstring adds a short name `-th` and a help message `A threshold parameter.` for threshold.

```python
def filter(self, x, threshold: float = 0.5):
    """
    
    Args:
        --threshold, -th: A threshold parameter.
    """
```

### Execute your CLI tool

Finally, import every subcommand classes to register parsers, and call `muli.exec()` to parse arguments and execute your subcommands.
If you forget to import any subcommands, the subcommands is not available.

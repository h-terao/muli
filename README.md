# multiprocess_cli
Easy to implement simple CLI tools with multiprocessing and progressbar.

## Usage

The following code is a minimal example.

```python
from multiprocess_cli import parser, Command

@parser.register()
class twice(Command):

    @staticmethod
    def process(v: int, bias: int = 0):
        print(2 * v + bias)

    @staticmethod
    def iterator(total: int):
        return range(total)    

if __name__ == "__main__":
    parser.run()
```

```bash
python twice.py twice --bias 1 --total 19 
```
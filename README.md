# multiprocess_cli
Easy to implement simple CLI tools with multiprocessing and progressbar.
This project is now in progress.

## Requirements
- python3
- tqdm
- docstring_parser

## Install
```bash 
pip install git+https://github.com/h-terao/multiprocess_cli
```

## Usage

### Example

Let's implement a simple CLI tool that doubles or halves values from zero to `total`. 
Write the following lines and save as `main.py`.

```python
from multiprocess_cli import parser, Command

@parser.register()
class double(Command):

    #
    #  Main function. You must implement this function.
    #  This function works in parallel.
    #
    @staticmethod
    def process(v: int):
        print(2 * v)

    #
    #  This function yields values to process. You must implement this function.
    #  Each yielded value is passed to process and filter.
    #
    def iterator(self, total: int):
        """ iterator function

        You can add help messages and short option by adding docstring. 

        Args:
            --total, -n (int): Total number of integers to process.
        """
        return range(total)

    #
    #  Filter function. This is optional to implement.
    #  If this function returns False, the value is skipped. 
    #
    def filter(self, x, foo: int = 10, bar: int = 20):
        """  filter function

        Args:
            foo (int): This is optional argument.
            bar (int): This is optional arugment.
        """
        return True

@parser.register()
class Halve(double):
    
    name = "halve"  # you can also register command name by adding a name attribute.
    
    @staticmethod
    def process(v: int):
        print(v / 2)


if __name__ == "__main__":
    parser.run()
```

Now, double and halve are prepared for multiprocessing.
We can call twice or halve with five workers from CLI:

```bash
python main.py twice --total 10 --workers 5 # 0, 2, 4, ...
python main.py halve --total 10 --workers 5 # 0, 0.5, 1, ...
```

### Add options

By implementing process, iterator, or filter methods to accept arguments, you can add CLI options.
If default values are not given, the argument will be required option. In addition, you can add help message or short name (e.g., --total, -n) by writing docstring.

```python
class Example(Command):

    # Add input option. This is required option.
    # In addition, you can see help message of --input option via --help.
    def iterator(self, input: Path):
        """ iterator.

        --input, -i (Path): Path to the input file.
        """
        with open(input, "r") as f:
            yield f

    # Add two options: a and b. They are optional.
    @staticmethod
    def process(x, a: int = 10, b: float = 0.1):
        ...

    # Add ignore_file option. This is optional.
    def filter(x, ignore_file: Path = None):
        ...
```

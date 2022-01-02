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

Let's implement a simple CLI tool that doubles or halves values from zero to `total`. 
Write the following lines and save as `main.py`.

```python
from multiprocess_cli import parser, Command


class Base(Command):

    @staticmethod
    def iterator(total: int):
        return range(total)


@parser.register()
class double(Base):

    @staticmethod
    def process(v: int):
        print(2 * v)


@parser.register()
class halve(Base):

    @staticmethod
    def process(v: int):
        print(v / 2)


if __name__ == "__main__":
    parser.run()
```

Now, we can call twice or halve from CLI:

```bash
python main.py twice --total 10  # 0, 2, 4, ...
python main.py halve --total 10  # 0, 0.5, 1, ...
```

### Add help messages or short name.

You can add help messages and short name by writing docstring.
For example, the following example setups default value, short name of arguments, and a help message of `--argument`.

```python
class double(Base):
    """ Double the sprcified values.
    """
    @staticmethod
    def process(v: int, argument: int = 0):  # set default value of a=0 
        """ process function.

        Args:
            --argument, -a (int): Additional argument.
        """
        print(2*v)
```


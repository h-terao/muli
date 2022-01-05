from muli import parser, Command


@parser.register()
class FizzBuzz(Command):
    """ FizzBuzz CLI tool
    """
    def glob(self, total: int = 100):
        return range(total)

    @staticmethod
    def process(value):
        if value % 15 == 0:
            print("FizzBuzz")
        elif value % 3 == 0:
            print("Fizz")
        elif value % 5 == 0:
            print("Buzz")
        else:
            print(value)


if __name__ == "__main__":
    parser.run()

from muli import exec, parser, Command


@parser.register()
class FizzBuzz(Command):
    """ FizzBuzz CLI tool
    """
    def glob(self, total: int = 100):
        return range(total)

    @staticmethod
    def step(value):
        if value % 15 == 0:
            print("FizzBuzz")
        elif value % 3 == 0:
            print("Fizz")
        elif value % 5 == 0:
            print("Buzz")
        else:
            print(value)


# @parser.register()
# class Error(Command):

#     @staticmethod
#     def step(v):
#         print(v)

#     def __init__(self, n_jobs: int = -1, x: str = "abc"):
#         super().__init__(n_jobs)
#         self.x = x

#     def postprocess(self, results, x: str = "z"):
#         return super().postprocess(results)


if __name__ == "__main__":
    exec()

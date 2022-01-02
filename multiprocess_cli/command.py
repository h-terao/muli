class Command:
    @staticmethod
    def process():
        raise NotImplementedError

    def iterator(self):
        raise NotImplementedError

    @staticmethod
    def filter(x) -> bool:
        return True 
        
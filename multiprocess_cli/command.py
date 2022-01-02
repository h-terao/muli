class Command:
    @staticmethod
    def process():
        raise NotImplementedError

    @staticmethod    
    def iterator():
        raise NotImplementedError

    @staticmethod
    def filter(x) -> bool:
        return True 
        
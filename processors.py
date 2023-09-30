class Processor:
    def __init__(self,key = ''):
        self.key = key
    def process(self,soup):
        soup.get_find_all(self.key)
import itertools
from wordlist import Loader

class AlterWords:
    def __init__(self, max_numbers_in_a_row=2, max_symbols=2):
        self.max_numbers_in_a_row = max_numbers_in_a_row
        self.max_symbols = max_symbols
        self.numbers = ['0','1','2','3','4','5','6','7','8','9']
        self.symbols = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+','[',']','{','}',';',':','"',"'","<",">",",",".","?","/","|","\\"]

    def add_numbers_symbols(self, word, add_numbers=True, add_symbols=True):
        variations = set()
        adjust_word_list = [word]
        
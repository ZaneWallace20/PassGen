import itertools
from wordlist import Loader

class AlterWords:
    def __init__(self, max_numbers_in_a_row=3, max_symbols=2):
        self.max_numbers_in_a_row = max_numbers_in_a_row
        self.max_symbols = max_symbols
        self.numbers = ['0','1','2','3','4','5','6','7','8','9']
        self.symbols = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+','[',']','{','}',';',':','"',"'","<",">",",",".","?","/","|","\\"]

    def add_numbers_symbols(self, add_numbers=True, add_symbols=True):
        variations = set()
        adjust_word_list = []

        numbers_to_add = [''.join(combo) for combo in itertools.permutations(self.numbers,self.max_numbers_in_a_row)]

        if numbers_to_add != 1:
            numbers_to_add += [num * self.max_numbers_in_a_row for num in self.numbers]

        total_size = self.max_symbols + 1
        for i in range(total_size):
            temp_word_list_full =[]
            for num in numbers_to_add:
                temp_word_list = [""] * total_size
                temp_word_list[i] = num      
                temp_word_list_full.append(temp_word_list)
            adjust_word_list.append(temp_word_list_full)

        for word_variation in len(adjust_word_list[0]):
            total_pos = []
x = AlterWords(max_numbers_in_a_row=2)
x.add_numbers_symbols(True, True)

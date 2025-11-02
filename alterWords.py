import itertools
import gc

class AlterWords:
    def __init__(self, max_numbers_in_a_row=3, min_symbols=1, max_symbols=2):
        self.max_numbers_in_a_row = max_numbers_in_a_row
        self.min_symbols = min_symbols
        self.max_symbols = max_symbols
        
        self.numbers = ['0','1','2','3','4','5','6','7','8','9']
        self.symbols = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+',
                        '[',']','{','}',';',':','"',"'","<",">",",",".","?","/","|","\\","`","~"]

    def add_numbers_symbols(self):
        adjust_word_list = []

        # gen number combinations
        numbers_to_add = [''.join(combo) for combo in itertools.permutations(self.numbers, self.max_numbers_in_a_row)]

        # adds n amount of the same number ie 00,11,22...
        numbers_to_add.extend([num * self.max_numbers_in_a_row for num in self.numbers])

        total_size = self.max_symbols + 1  

        for i in range(total_size):
            temp_word_list_full = []
            for num in numbers_to_add:
                temp_word_list = [""] * total_size
                temp_word_list[i] = num
                temp_word_list_full.append(temp_word_list.copy())
            adjust_word_list.append(temp_word_list_full.copy())


        # generate all symbol combinations of n length from min_symbols to max_symbols
        all_symbol_combos = []
        for length in range(self.min_symbols, self.max_symbols + 1):
            all_symbol_combos.extend(itertools.permutations(self.symbols, length))

        # add n amount of the same symbol ie !!,@@,##
        all_symbol_combos.extend([symbol * self.max_symbols for symbol in self.symbols])
        
        # generate all combinations of numbers and symbols
        # fits the form of ["number","symbol","symbol"], ["symbol","number","symbol"], etc.
        final_combos = []
        for index_list in adjust_word_list:
            for position_list in index_list:
                for symbol_combo in all_symbol_combos:
                    filled = position_list.copy()
                    sym_index = 0
                    for k in range(len(filled)):
                        if filled[k] == "" and sym_index < len(symbol_combo):
                            # used when min/max symbols dont match
                            if symbol_combo[sym_index] == '':
                                continue
                            filled[k] = symbol_combo[sym_index]
                            sym_index += 1

                            

                    final_combos.append(filled)

        print(f"Total generated: {len(final_combos)}")
        gc.collect()
        return final_combos

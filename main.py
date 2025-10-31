from alterWords import AlterWords
from wordlist import Loader
alter = AlterWords(max_numbers_in_a_row=2, min_symbols=1, max_symbols=2)

combos = alter.add_numbers_symbols()


words = Loader('words.txt').load_words()

data_to_write = []



for word in words:
    for combo in combos:
        for index in range(len(combo)+1):
            combo_copy = combo.copy()
            combo_copy.insert(index, word)
            data_to_write.append(''.join(combo_copy))

with open('altered_words.txt', 'w') as f:
    for item in data_to_write:
        f.write("%s\n" % item)
        
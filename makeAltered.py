from itertools import product, permutations
import json
from wordlist import Loader

class WordlistGenerator:

    def __init__(self):
        with open("passConfig.json", "r") as f:
            config = json.load(f)
            self.passStyle = config.get("passwordStyle")
            self.should_permute = config.get("permutate", False)
        with open("config.json", "r") as f:
            config = json.load(f)
            self.numbers = config.get("numbers", [])
            self.symbols = config.get("symbols", [])
            wordlist_file = config.get("wordlistFile", "wordlist.txt")


        self.words = Loader(wordlist_file).load_words()

    def _generate_format(self):
        
        result = []
        if not isinstance(self.passStyle, list):
            return result

        for part in self.passStyle:
            min_amt = part.get("minAmount", 0)
            max_amt = part.get("maxAmount", min_amt)

            t = part.get("type", "").lower()
            if t == "word":
                tokens = ['']
            elif t in ("symbols", "symbol"):
                tokens = list(self.symbols)
            elif t in ("number", "numbers"):
                tokens = list(self.numbers)
            else:
                tokens = []

            result.append({
                "tokens": tokens,
                "minAmount": min_amt,
                "maxAmount": max_amt,
            })

        return result

    def _save_to_disk(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"\n{item}")

    def _generate_altered_list(self):
        format = self._generate_format()

        count_ranges = [range(dict["minAmount"], dict["maxAmount"] + 1) for dict in format]
        all_combinations = []
        print(count_ranges)
        for counts in product(*count_ranges):
            part_lists = []

            for part, count in zip(format, counts):
                
                tokens = part.get("tokens", [])
                if count == 0:
                    part_lists.append([""])
                    continue

                combos = ["".join(tpl) for tpl in product(tokens, repeat=count)]
                part_lists.append(combos)

            for choice_tuple in product(*part_lists):
                if self.should_permute:
                    for perm in permutations(choice_tuple):
                        all_combinations.append(list(perm))
                else:
                    all_combinations.append(list(choice_tuple))

        return all_combinations


W = WordlistGenerator()
combos = W.generate_altered()
for combo in combos:    
    print(combo)
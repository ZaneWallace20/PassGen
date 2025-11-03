from itertools import product, permutations
from concurrent.futures import ProcessPoolExecutor
import json
from wordlist import Loader
import numpy as np
import os
import uuid

class WordlistGenerator:

    def __init__(self, numbers=None, symbols=None, wordlist_file='wordlist.txt', max_batch_size=2_000_000, max_threads=-1, folder_path='Wordlists'):

        # Read pass configuration here (allowed per request)
        config_path = os.path.join("Configs", "passConfig.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            self.passStyle = config.get("passwordStyle")
            # note: passConfig.json has a misspelled key in the sample; keep the old key for backwards compatibility
            self.should_permute = config.get("permutate", config.get("perumtate", False))

        # The remaining values come from the main config and should be passed in by the caller
        self.numbers = numbers or []
        self.symbols = symbols or []
        self.max_batch_size = max_batch_size
        self.max_threads = max_threads
        self.folder_path = folder_path

        self.word_indicator = uuid.uuid4().hex
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
                tokens = [self.word_indicator]
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

  

    def _threaded_function(self, combo_list, max_batch_size, thread_name):
        
        print(f"Thread {thread_name} started with {len(combo_list)} combinations.")
        result_list = []
        current_count = 0
        for combo in combo_list:
            combo = list(combo)
            amount_to_add = combo.count(self.word_indicator)
            perms = list(product(self.words, repeat=amount_to_add))
            for perm in perms:
                temp_combo = combo.copy()
                index = 0
                while self.word_indicator in temp_combo:
                    word_to_add = perm[index]
                    temp_combo[temp_combo.index(self.word_indicator)] = word_to_add
                    index += 1
                
                final = ''.join(temp_combo)

                result_list.append(final)
                if len(result_list) >= max_batch_size:
                    path = os.path.join(self.folder_path, f'temp_altered_words_{thread_name}_{current_count + 1}.txt')
                    print(f"Thread {thread_name} saving {len(result_list)} words to {path}...")
                    self._save_to_disk(path, result_list)
                    result_list.clear()
                    current_count += 1 
    
        # if any left
        if result_list:
            path = os.path.join(self.folder_path, f'temp_altered_words_{thread_name}_{current_count + 1}.txt')
            print(f"Thread {thread_name} saving {len(result_list)} words to {path}...")
            self._save_to_disk(path, result_list)
            result_list.clear()

    def _generate_altered_list(self):
        format = self._generate_format()

        count_ranges = [range(dict["minAmount"], dict["maxAmount"] + 1) for dict in format]
        all_combinations = []

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
    

    def make_and_save_wordlist(self):

        if os.path.exists(self.folder_path):
            print(f"Folder {self.folder_path} already exists.")
            print("Please remove or rename the existing folder and try again.")
            return
        else:
            os.makedirs(self.folder_path, exist_ok=True)
        # Determine number of threads to use
        if isinstance(self.max_threads, int) and self.max_threads > 0:
            num_threads = self.max_threads
        else:
            num_threads = os.cpu_count() or 4
        combos = self._generate_altered_list()
        chunks = np.array_split(combos, num_threads)

        print("Processing words in threads...")
        try:
            approx_count = len(chunks[0])
        except Exception:
            approx_count = 0
        print(f"Using {num_threads} threads with {approx_count} combinations each (approx).")
        current_thread_name  = [i+1 for i in range(num_threads)]

        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            executor.map(
                self._threaded_function,
                chunks,
                [self.max_batch_size] * num_threads,
                current_thread_name
        )
            
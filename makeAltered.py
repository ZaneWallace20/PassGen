from itertools import product, permutations
from concurrent.futures import ProcessPoolExecutor
import json
from wordlist import Loader
import numpy as np
import os
import shutil
import uuid

class WordlistGenerator:

    def __init__(self, numbers=None, symbols=None, wordlist_file='wordlist.txt', max_batch_size=2_000_000, max_threads=-1, folder_path='Wordlists', pass_config_extra="0"):

        config_path = os.path.join("Configs", f"passConfig{pass_config_extra}.json")
        with open(config_path, "r") as f:
            config = json.load(f)
            self.passStyle = config.get("passwordStyle")
            self.permute_indices = config.get("permutate", config.get("permutate", []))

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
            elif t == "custom":
                tokens = [part.get("word", "")]
            else:
                tokens = []

            result.append({
                "tokens": tokens,
                "minAmount": min_amt,
                "maxAmount": max_amt,
            })

        return result
    def _save_to_disk(self, path, data):
        with open(path, 'a', encoding='utf-8') as f:  
            for item in data:
                f.write(f"\n{item}")

    def _threaded_function(self, combo_list, max_batch_size, thread_name):
        print(f"Thread {thread_name} started with {len(combo_list)} combinations.")
        
        result_list = []
        seen = set()
        output_path = os.path.join(self.folder_path, f"altered_words_{thread_name}.txt")
        
        for combo in combo_list:
            combo = list(combo)
            amount_to_add = combo.count(self.word_indicator)
            perms = product(self.words, repeat=amount_to_add)

            for perm in perms:
                temp_combo = combo.copy()
                index = 0
                while self.word_indicator in temp_combo:
                    word_to_add = perm[index]
                    temp_combo[temp_combo.index(self.word_indicator)] = word_to_add
                    index += 1
                
                final = ''.join(temp_combo)
                if final in seen:
                    continue  
                seen.add(final)
                result_list.append(final)
                
                if len(result_list) >= max_batch_size:
                    self._save_to_disk(output_path, result_list)
                    seen.clear()
                    result_list.clear()

        # any left 
        if result_list:
            self._save_to_disk(output_path, result_list)

        print(f"Thread {thread_name} finished writing to {output_path}.")


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
                choice_list = list(choice_tuple)

                if self.permute_indices:
                    items_to_permute = [choice_list[i] for i in self.permute_indices]

                    for item in items_to_permute:
                        temp_choice_list = choice_list.copy()
                        choice_list.remove(item)
                        for i in range(len(choice_list)+1):
                            new_choice = choice_list.copy()
                            new_choice.insert(i, item)
                            all_combinations.append(new_choice)
                                
                        choice_list = temp_choice_list
                else:
                    all_combinations.append(choice_list)
        return all_combinations
    

    def make_and_save_wordlist(self):

        if os.path.exists(self.folder_path):
            print(f"Folder {self.folder_path} already exists.")
            print("Clearing out...")
            shutil.rmtree(self.folder_path)

            
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
            
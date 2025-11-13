from itertools import product
from concurrent.futures import ProcessPoolExecutor
import json
from wordlist import Loader
import numpy as np
import os
import shutil
import uuid

class WordlistGenerator:

    def __init__(self,  wordlist_file='wordlist.txt', max_batch_size=2_000_000, max_threads=-1, folder_path='Wordlists', config_path=os.path.join("Configs","TestPassConfigs","passConfig.json")):

        print(f"Loading pass configuration from {config_path}...")
        with open(config_path, "r") as f:
            config = json.load(f)
            self.passStyle = config.get("passwordStyle")
            self.permutation_indices = config.get("permutations", [])

        with open(os.path.join("Configs", "types.json"), "r") as f:
            self.types = json.load(f)
        self.max_batch_size = max_batch_size
        self.max_threads = max_threads
        self.folder_path = folder_path

        self.word_indicator = uuid.uuid4().hex
        if wordlist_file != "":
            self.words = Loader(wordlist_file).load_words()
        else:
            self.words = []

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
            elif t == "custom":
                tokens = [part.get("word", "")]
            else:
                tokens = self.types.get(t, [])
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


    # takes the combos (stuff like ['!!', 'word_indicator', '123']) and makes the final words by replacing the word indicators with actual words
    def _threaded_function(self, combo_list, max_batch_size, thread_name):
        print(f"Thread {thread_name} started with {len(combo_list)} combinations.")
        
        result_list = []
        output_path = os.path.join(self.folder_path, f"altered_words_{thread_name}.txt")

        this_combo_list = combo_list.copy()  # Convert numpy array to list if necessary 
        for combo in this_combo_list:


            # check amount of word indicators in combo
            amount_to_add = 0 
            for item in combo:
                print(item)
                if item == self.word_indicator:
                    amount_to_add += 1

            perms = product(self.words, repeat=amount_to_add)
            for perm in perms:
                temp_combo = combo.copy()
                indices = [i for i, x in enumerate(temp_combo) if x == self.word_indicator]
                index = 0
                while self.word_indicator in temp_combo:
                    word_to_add = perm[index]
                    temp_combo[indices[index]] = word_to_add
                    index += 1
                
                final = ''.join(temp_combo)
                result_list.append(final)
                
                if len(result_list) >= max_batch_size:
                    self._save_to_disk(output_path, result_list)
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

                combos = []
                
                # use for words being unique
                for tpl in product(tokens, repeat=count):


                    '''
                    words are uniuqe, how they work is we set a UUID as a token,
                    this token is then replaced with actual words later on in the threaded function,
                    however if there are multiple word indicators in a tpl, we need to keep them as separate items in a list
                    in the normal way it would be UUIDUUID but we need [UUID, UUID] so we can replace them with different words later on
                    however if this were just appended the permutations would be messde upas the index of the words would be off

                    ie

                    tpl = (word_indicator, word_indicator, '123')
                    over
                    tpl = ((word_indicator, word_indicator), '123')
                    

                    now the the permutaions are kept correct as the word indicators are separate items in the list

                    '''
                    if tokens == [self.word_indicator]:
                        combo = []
                        
                        for word in tpl: 
                            combo.append(word)
                        combos.append(combo)
                    else:
                        combos.append("".join(tpl))

                part_lists.append(combos)
            for choice_tuple in product(*part_lists):
                choice_list = list(choice_tuple)

            #if there are permutation indices, permute those items in all possible positions
            # ex: if indices are [0,2] and choice_list is ['a','b','c','d'], we permute 'a' and 'c' in all possible positions
            # resulting in ['a','b','c','d'], ['c','b','a','d'], ['b','a','c','d'], etc.
            if self.permutation_indices:
                items_to_permute = [choice_list[i] for i in self.permutation_indices]
                
                for item in items_to_permute:
                    temp_choice_list = choice_list.copy()
                    choice_list.remove(item)
                    for i in range(len(choice_list)+1):
                        new_choice = choice_list.copy()
                        new_choice.insert(i, item)
                        temp_choice = []

                        '''
                        flatten the new_choice list in case there are lists inside (from word indicators)
                        ex: new_choice = ['a', [word_indicator, word_indicator], 'b']
                        becomes temp_choice = ['a', word_indicator, word_indicator, 'b']
                        this is as threaded function expects a flat list
                        '''
                        for choice in new_choice:
                            if isinstance(choice, list):
                                temp_choice.extend(choice)
                            else:
                                temp_choice.append(choice)
                            
                        all_combinations.append(temp_choice)
                            
                    choice_list = temp_choice_list
            else:
                temp_choice = []
                for choice in choice_list:
                    if isinstance(choice, list):
                        temp_choice.extend(choice)
                    else:
                        temp_choice.append(choice)
                all_combinations.append(temp_choice)

        final_list = []
        seen = set()
        # remove duplicates
        for combo in all_combinations:
            t = tuple(combo)
            if t not in seen:
                seen.add(t)
                final_list.append(combo)
                
        return final_list
    

    # the public func 
    def make_and_save_wordlist(self):

        # Prepare output folder
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

        # threaded processing
        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            executor.map(
                self._threaded_function,
                chunks,
                [self.max_batch_size] * num_threads,
                current_thread_name
        )
            
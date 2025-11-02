from alterWords import AlterWords
import time
import gc
from wordlist import Loader
from concurrent.futures import ProcessPoolExecutor
import os
import json
import subprocess
import numpy as np

class PassGen:
    def __init__(self, config_path='config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Use config values with sensible defaults
        self.wordlist_file = self.config.get('wordlistFile')
        self.max_threads = self.config.get('maxThreads', -1)
        self.max_batch_size = self.config.get('maxBatchSize', 2_000_000)
        self.folder_path = self.config.get('wordlistsFolder', 'Wordlists')

        self.alter = AlterWords(
            max_numbers_in_a_row=self.config.get("maxNumbersInARow", 1),
            min_symbols=self.config.get("minSymbols", 1),
            max_symbols=self.config.get("maxSymbols", 1)
        )

        self.combos = self.alter.add_numbers_symbols()
        self.words = Loader(self.wordlist_file).load_words()

    def save_to_disk(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"\n{item}")

    # ram destroyer D:
    def threaded_function(self, word_list, max_batch_size, folder, thread_name):
        print(f"Thread {thread_name} starting with {len(word_list)} words...")
        try:
            result_list = []
            current_count = 0

            for word in word_list:
                for combo in self.combos:
                    for index in range(len(combo) + 1):
                        new_combo = combo[:index] + [word] + combo[index:]
                        result_list.append(''.join(new_combo))

                        if len(result_list) >= max_batch_size:
                            path = os.path.join(folder, f'temp_altered_words_{thread_name}_{current_count + 1}.txt')
                            print(f"Thread {thread_name} saving {len(result_list)} words to {path}...")
                            self.save_to_disk(path, result_list)
                            result_list.clear()
                            current_count += 1

            # if any left 
            if result_list:
                path = os.path.join(folder, f'temp_altered_words_{thread_name}_{current_count + 1}.txt')
                self.save_to_disk(path, result_list)
                result_list.clear()
        except Exception as e:
            print(f"Error in thread {thread_name}: {e}")

    def run(self):
        total_start = time.time()
        if os.path.exists(self.folder_path):
            print(f"Folder {self.folder_path} already exists.")
        else:
            
            os.makedirs(self.folder_path, exist_ok=True)
            self.start_threads()
        
        self.run_hashcat()
        total_end = time.time()
        print(f"Total execution time: {total_end - total_start} seconds.")

    def start_threads(self):
        current_time = time.time()

        # Determine number of threads to use
        if isinstance(self.max_threads, int) and self.max_threads > 0:
            num_threads = self.max_threads
        else:
            num_threads = os.cpu_count() or 4

        print(f"Using {num_threads} threads for processing.")

        total_words = len(self.words)
        if total_words == 0:
            print("No words to process. Exiting.")
            return

        chunks = np.array_split(self.words, num_threads)
        chunk_size = len(chunks[0])

        print("Processing words in threads...")
        print(f"Total words: {total_words}, Chunk size: {chunk_size}")

        current_thread_name  = [i+1 for i in range(num_threads)]

        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            executor.map(
                self.threaded_function,
                chunks,
                [self.max_batch_size] * num_threads,
                [self.folder_path] * num_threads,
                current_thread_name
        )

        done_time = time.time()

        print(f"All threads have completed in {done_time - current_time} seconds.")

    def run_hashcat(self):
        print("Running hashcat...")

        hashes_path = os.path.join(os.getcwd(), self.config.get("hashFile", "hashes.txt"))
        output_path = os.path.join(os.getcwd(), self.config.get("outputFile", "cracked.txt"))
        print(output_path)
        # runs mr cat over the massive wordlist in directory
        hashcat_cmd = [
            "hashcat",
            "-m", str(self.config.get("hashType", 0)),
            "-a", "0",
            hashes_path,
            os.path.join(os.getcwd(), self.folder_path)
        ]

        print("Executing Hashcat command: ", hashcat_cmd)
        hashcat_path = self.config.get("pathToHashcatFolder", os.getcwd())
        subprocess.run(hashcat_cmd, cwd=hashcat_path)

        hashcat_cmd = [
            "hashcat",
            "--show",
            "-m", str(self.config.get("hashType", 0)),
            "-o", output_path,
            hashes_path,
        ]

        hashcat_path = self.config.get("pathToHashcatFolder", os.getcwd())
        subprocess.run(hashcat_cmd, cwd=hashcat_path)
        print("Hashcat run completed.")


if __name__ == "__main__":  
    PassGen().run()
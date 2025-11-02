from alterWords import AlterWords
import time
import gc
from wordlist import Loader
import threading
import os
import json
import subprocess

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
                f.write("%s\n" % item)

    # ram destroyer D:
    def threaded_function(self, word_list, max_batch_size, folder):
        try:
            result_list = []
            current_count = 0
            for word in word_list:
                for combo in self.combos:
                    for index in range(len(combo) + 1):
                        combo_copy = combo.copy()
                        combo_copy.insert(index, word)
                        result_list.append(''.join(combo_copy))

                        if len(result_list) >= max_batch_size:
                            path = os.path.join(folder, f'temp_altered_words_{threading.get_ident()}_{current_count + 1}.txt')
                            print(f"Thread {threading.get_ident()} saving {len(result_list)} words to {path}...")
                            self.save_to_disk(path, result_list)
                            gc.collect()
                            result_list.clear()
                            current_count += 1

            # Save any remaining
            path = os.path.join(folder, f'temp_altered_words_{threading.get_ident()}_{current_count + 1}.txt')
            print(f"Thread {threading.get_ident()} saving {len(result_list)} words to {path}...")
            self.save_to_disk(path, result_list)
            gc.collect()
            result_list.clear()
        except Exception as e:
            print(f"Error in thread {threading.get_ident()}: {e}")
    def run(self):



        if os.path.exists(self.folder_path):
            print(f"Folder {self.folder_path} already exists.")
        else:
            
            os.makedirs(self.folder_path, exist_ok=True)
            self.start_threads()
        
        self.run_hashcat()

    def start_threads(self):
        current_time = time.time()

        # Determine number of threads to use
        if isinstance(self.max_threads, int) and self.max_threads > 0:
            num_threads = self.max_threads
        else:
            num_threads = os.cpu_count() or 4

        print(f"Using {num_threads} threads for processing.")

        threads = []
        total_words = len(self.words)
        if total_words == 0:
            print("No words to process. Exiting.")
            exit(0)

        chunk_size = max(1, total_words // num_threads)


        print("Processing words in threads...")
        print(f"Total words: {total_words}, Chunk size: {chunk_size}")

        for i in range(num_threads):
            start = i * chunk_size

            # end check
            end = -1 if i == num_threads - 1 else (i + 1) * chunk_size
            chunk = self.words[start:end]
            thread = threading.Thread(target=self.threaded_function, args=(chunk, self.max_batch_size, self.folder_path))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
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
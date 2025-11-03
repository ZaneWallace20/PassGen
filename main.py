from makeAltered import WordlistGenerator
from hashcatRunner import HashcatRunner
import time
import os
import json

class PassGen:
    def __init__(self, config_path=None):

        base_dir = os.getcwd()
        if config_path is None:
            config_path = os.path.join(base_dir, 'Configs', 'config.json')

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.numbers = self.config.get('numbers', [])
        self.symbols = self.config.get('symbols', [])
        self.wordlistFile = self.config.get('wordlistFile', 'wordlist.txt')
        self.max_batch_size = self.config.get('maxBatchSize', 2_000_000)
        self.max_threads = self.config.get('maxThreads', -1)
        self.folder_path = self.config.get('wordlistsFolder', 'Wordlists')
        self.pathToHashcatFolder = self.config.get('pathToHashcatFolder', base_dir)
        self.hashFile = self.config.get('hashFile', 'hashes.txt')
        self.outputFile = self.config.get('outputFile', 'cracked.txt')
        self.hashType = self.config.get('hashType', 0)
        self.passConfigAmount = self.config.get('passConfigAmount', 1)


    def run(self):
        total_start = time.time()
        for i in range(self.passConfigAmount):
            print(f"Starting pass configuration {i}...")
            # Instantiate WordlistGenerator with values read from main config
            wordlist_generator = WordlistGenerator(
                numbers=self.numbers,
                symbols=self.symbols,
                wordlist_file=self.wordlistFile,
                max_batch_size=self.max_batch_size,
                max_threads=self.max_threads,
                folder_path=self.folder_path,
                pass_config_extra=str(i)
            )

            hashcat_runner = HashcatRunner(
                output_file=self.outputFile,
                hash_file=self.hashFile,
                hash_type=self.hashType,
                folder_path=self.folder_path,
                hashcat_path=self.pathToHashcatFolder
            )

            wordlist_generator.make_and_save_wordlist()

            # Run hashcat using values pulled from config
            hashcat_runner.run_hashcat()    

            total_end = time.time()
        print(f"Total execution time: {total_end - total_start} seconds.")

if __name__ == "__main__":  
    PassGen().run()
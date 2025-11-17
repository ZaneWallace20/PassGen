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

        self.wordlist_file = self.config.get('wordlistFile', 'wordlist.txt')
        self.max_batch_size = self.config.get('maxBatchSize', 2_000_000)
        self.max_threads = self.config.get('maxThreads', -1)
        self.folder_path = self.config.get('wordlistsFolder', 'Wordlists')
        self.path_to_hashcat_folder = self.config.get('pathToHashcatFolder', base_dir)
        self.hash_file = self.config.get('hashFile', 'hashes.txt')
        self.output_file = self.config.get('outputFile', 'cracked.txt')
        self.hash_type = self.config.get('hashType', 0)
        self.passConfigsPath = self.config.get('passConfigPath', os.path.join(base_dir, 'Configs', 'passConfigs.json'))
        self.max_wordlist_size_gb = self.config.get('maxWordlistSizeGB', 20)

    def run(self):
        total_start = time.time()

        # Determine the number of pass configurations
        pass_configs = [os.path.join(self.passConfigsPath, name) for name in os.listdir(self.passConfigsPath) if name.endswith('.json')]
        for i in pass_configs:
            print(f"Starting pass configuration {i}...")
            hashcat_runner = HashcatRunner(
                output_file=self.output_file,
                hash_file=self.hash_file,
                hash_type=self.hash_type,
                folder_path=self.folder_path,
                hashcat_path=self.path_to_hashcat_folder
            )

            # Instantiate WordlistGenerator with values read from main config
            wordlist_generator = WordlistGenerator(
                hashcat=hashcat_runner,
                wordlist_file=self.wordlist_file,
                max_batch_size=self.max_batch_size,
                max_threads=self.max_threads,
                folder_path=self.folder_path,
                config_path=i,
                max_wordlist_size_gb=self.max_wordlist_size_gb
            )


            wordlist_generator.make_and_save_wordlist()

            # Run Mr. Cat using values pulled from config
            hashcat_runner.run_hashcat()    

        total_end = time.time()
        print(f"Total execution time: {total_end - total_start} seconds.")

if __name__ == "__main__":  
    PassGen().run()
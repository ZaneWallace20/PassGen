from alterWords import AlterWords
import time
import gc
from wordlist import Loader
import threading
import os
import json
import subprocess

with open('config.json', 'r') as f:
    config = json.load(f)


# Use config values with sensible defaults
wordlist_file = config.get('wordlistFile')
max_threads = config.get('maxThreads', -1)
max_batch_size = config.get('maxBatchSize', 2_000_000)
folder_path = config.get('wordlistsFolder', 'Wordlists')

alter = AlterWords(
    max_numbers_in_a_row=config.get("maxNumbersInARow", 1),
    min_symbols=config.get("minSymbols", 1),
    max_symbols=config.get("maxSymbols", 1)
)

def save_to_disk(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write("%s\n" % item)

# ram destroyer D:
def threaded_function(word_list, max_batch_size, folder):
    result_list = []
    current_count = 0
    for word in word_list:
        for combo in combos:
            for index in range(len(combo) + 1):
                combo_copy = combo.copy()
                combo_copy.insert(index, word)
                result_list.append(''.join(combo_copy))

                if len(result_list) >= max_batch_size:
                    path = os.path.join(folder, f'temp_altered_words_{threading.get_ident()}_{current_count + 1}.txt')
                    print(f"Thread {threading.get_ident()} saving {len(result_list)} words to {path}...")
                    save_to_disk(path, result_list)
                    gc.collect()
                    result_list.clear()
                    current_count += 1

    # Save any remaining
    path = os.path.join(folder, f'temp_altered_words_{threading.get_ident()}_{current_count + 1}.txt')
    print(f"Thread {threading.get_ident()} saving {len(result_list)} words to {path}...")
    save_to_disk(path, result_list)
    gc.collect()
    result_list.clear()

current_time = time.time()

# Determine number of threads to use
if isinstance(max_threads, int) and max_threads > 0:
    num_threads = max_threads
else:
    num_threads = os.cpu_count() or 4

print(f"Using {num_threads} threads for processing.")


combos = alter.add_numbers_symbols()
words = Loader(wordlist_file).load_words()

threads = []
total_words = len(words)
if total_words == 0:
    print("No words to process. Exiting.")
    exit(0)

chunk_size = max(1, total_words // num_threads)

if os.path.exists(folder_path):
    print(f"Folder {folder_path} already exists.")
    exit(1)
else:
    os.makedirs(folder_path, exist_ok=True)

print("Processing words in threads...")
print(f"Total words: {total_words}, Chunk size: {chunk_size}")

for i in range(num_threads):
    start = i * chunk_size

    # end check
    end = -1 if i == num_threads - 1 else (i + 1) * chunk_size
    chunk = words[start:end]
    thread = threading.Thread(target=threaded_function, args=(chunk, max_batch_size, folder_path))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()
done_time = time.time()

print(f"All threads have completed in {done_time - current_time} seconds.")

print("Running hashcat...")

hashes_path = os.path.join(os.getcwd(), config.get("hashFile", "hashes.txt"))
output_path = os.path.join(os.getcwd(), config.get("outputFile", "cracked.txt"))


# runs mr cat over the massive wordlist in directory
hashcat_cmd = [
"hashcat",
"-m", str(config.get("hashType", 0)),
"-a", "0",
hashes_path,
output_path,
os.path.join(os.getcwd(), folder_path)
]

hashcat_path = config.get("pathToHashcatFolder", os.getcwd())
subprocess.run(hashcat_cmd, cwd=hashcat_path)
print("Hashcat run completed.")
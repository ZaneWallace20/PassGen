from alterWords import AlterWords
import time
import gc
from wordlist import Loader
import threading
import os


alter = AlterWords(max_numbers_in_a_row=2, min_symbols=1, max_symbols=2)

combos = alter.add_numbers_symbols()


words = Loader('formatted_tv_shows.txt').load_words()

def save_to_disk(path, data):
    with open(path, 'w') as f:
        for item in data:
            f.write("%s\n" % item)

def threaded_function(word_list, max_batch_size=10_000_000, folder="Wordlists"):
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

    path = os.path.join(folder, f'temp_altered_words_{threading.get_ident()}_{current_count + 1}.txt')

    print(f"Thread {threading.get_ident()} saving {len(result_list)} words to {path}...")

    save_to_disk(path, result_list)

    gc.collect()
    result_list.clear()

num_threads = os.cpu_count() or 4

print(f"Using {num_threads} threads for processing.")

threads = []
chunk_size = len(words) // num_threads

folder_path = "Wordlists"
os.makedirs(folder_path, exist_ok=True)

for i in range(num_threads):
    chunk = words[i * chunk_size:(i + 1) * chunk_size]
    thread = threading.Thread(target=threaded_function, args=(chunk,))
    threads.append(thread)
    thread.start()

print("Processing words in threads...")

current_time = time.time()
for thread in threads:
    thread.join()
done_time = time.time()

print(f"All threads have completed in {done_time - current_time} seconds.")

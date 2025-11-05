import os
class Loader:
    def __init__(self, filepath = 'words.txt', tested_filepath = None):
        self.filepath = filepath
        self.tested_filepath = tested_filepath

    def _grab_previously_tested(self):
        
        tested_words = set()
        if self.tested_filepath and os.path.exists(self.tested_filepath):
            with open(self.tested_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        tested_words.add(word)
        return tested_words 

    def _format_word(self, word):
        word = word.strip()
        word = word.replace(" ","")

        # remove duplicates
        return list(set([word, word.lower(), word.upper()]))

    def load_words(self):
        tested_words = self._grab_previously_tested()
        wordlist_set = set()
        with open(self.filepath, 'r') as file:
            for line in file:
                word = line.strip()
                if word and word not in tested_words:
                    wordlist_set.add(word)
        words = [formattedWord for word in wordlist_set for formattedWord in self._format_word(word)]
        
        print(f"Loaded {len(words)} unique words from {self.filepath}")
        return words

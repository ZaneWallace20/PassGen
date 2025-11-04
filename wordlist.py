class Loader:
    def __init__(self, filepath = 'words.txt'):
        self.filepath = filepath

    def _format_word(self, word):
        word = word.strip()
        word = word.replace(" ","")

        # remove duplicates
        return list(set([word, word.lower(), word.upper()]))

    def load_words(self):
        with open(self.filepath, 'r') as file:
            
            words = list(set([formattedWord for line in file if line.strip() for formattedWord in self._format_word(line)]))
        
        print(f"Loaded {len(words)} unique words from {self.filepath}")
        return words

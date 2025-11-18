import subprocess
import os
class HashcatRunner:
    def __init__(self, output_file, hash_file, hash_type, folder_path, hashcat_path=os.getcwd()):
        self.output_file = output_file
        self.hash_file = hash_file
        self.hash_type = hash_type
        self.folder_path = folder_path
        self.hashcat_path = hashcat_path
        self.is_hashing = False
    def run_hashcat(self):
        print("Running hashcat...")

        hashes_path = os.path.join(os.getcwd(), self.hash_file)
        output_path = os.path.join(os.getcwd(), self.output_file)
        
        # runs hashcat over the massive wordlist in directory
        hashcat_cmd = [
            "hashcat",
            "-m", str(self.hash_type),
            "-a", "0",
            hashes_path,
            os.path.join(os.getcwd(), self.folder_path)
        ]

        print("Executing Hashcat command: ", hashcat_cmd)
        print("Hashcat path: ", self.hashcat_path)
        subprocess.run(hashcat_cmd, cwd=self.hashcat_path)

        # clear output file
        with open(output_path, 'w') as f:
            f.write('')
            
        # save
        hashcat_cmd = [
            "hashcat",
            "--show",
            "-m", str(self.hash_type),
            "-o", output_path,
            hashes_path,
        ]

        subprocess.run(hashcat_cmd, cwd=self.hashcat_path)
        print("Hashcat run completed.")

    def run_hashcat_on_file(self, wordlist_file):

        print(f"Running hashcat on {wordlist_file}...")

        hashes_path = os.path.join(os.getcwd(), self.hash_file)
        output_path = os.path.join(os.getcwd(), self.output_file)
        wordlist_file = os.path.join(os.getcwd(), wordlist_file) 
        
        # runs hashcat over the massive wordlist FILE 
        hashcat_cmd = [
            "hashcat",
            "--logfile-disable",
            "-m", str(self.hash_type),
            "-a", "0",
            hashes_path,
            wordlist_file
        ]

        print("Executing Hashcat command: ", hashcat_cmd)
        print("Hashcat path: ", self.hashcat_path)
        subprocess.run(hashcat_cmd, cwd=self.hashcat_path)

        # clear output file
        with open(output_path, 'w') as f:
            f.write('')
            
        # save
        hashcat_cmd = [
            "hashcat",
            "--show",
            "-m", str(self.hash_type),
            "-o", output_path,
            hashes_path,
        ]

        subprocess.run(hashcat_cmd, cwd=self.hashcat_path)
        
        # clear wordlist file
        with open(wordlist_file, 'w', encoding='utf-8') as f:
            f.write('')

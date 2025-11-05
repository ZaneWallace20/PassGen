import subprocess
import os
class HashcatRunner:
    def __init__(self, output_file, hash_file, hash_type, folder_path, hashcat_path=os.getcwd()):
        self.output_file = output_file
        self.hash_file = hash_file
        self.hash_type = hash_type
        self.folder_path = folder_path
        self.hashcat_path = hashcat_path
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

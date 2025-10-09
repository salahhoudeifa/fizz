import random
import string
import subprocess
import os
import pathlib
from pathlib import Path

# Generation-based fuzz

class Fuzzer:
    def __init__(self, target, num_iterations, crashes):
        self.target = target
        self.num_iterations = num_iterations
        self.crashes = []
        self.unique_inputs = set()

    def generate(self):
        length = random.randint(1, 32)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def run(self, target):
        try:   
            target_name, target_extension = os.path.splitext(os.path.basename(target))
            generated_input = self.generate()
            if target_extension == '.py':
                result = subprocess.run(["python", target], input=generated_input.encode(), capture_output=True, timeout=1)
            else:
                result = subprocess.run([target], input=self.generate().encode(), capture_output=True, timeout=1)
            return result.returncode, result.stdout, result.stderr, generated_input
        except subprocess.TimeoutExpired:
            print("Process timed out")
            return -1, b'', b'Timeout', None
        
    def fuzz(self):
        
        for i in range (self.num_iterations):
            if i % 100 == 0:
                print(f"Progress: {i+1}/{self.num_iterations}")
            retcode, stdout, stderr, finput = self.run(self.target)
            if retcode != 0:
                print(f"Crash detected! Return code: {retcode}")
                print(f"Stdout: {stdout.decode()}")
                print(f"Stderr: {stderr.decode()}")
            else: # Store valid inputs for later use
                corpus_dir = Path.cwd() / 'corpus'
                if not corpus_dir.exists():
                    corpus_dir.mkdir()
                if finput not in self.unique_inputs:
                    self.unique_inputs.add(finput)
                    with open(f"corpus/input_{i}.txt", "w") as f:
                        f.write(finput)

            self.crashes.append((retcode, stdout, stderr))
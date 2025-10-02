import random
import string
import subprocess
import time
import os
import pathlib

# Generation-based fuzz

class Fuzzer:
    def __init__(self, target, num_iterations, crashes):
        self.target = target
        self.num_iterations = num_iterations
        self.crashes = []

    def generate(self):
        length = random.randint(1, 32)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def run(self, target):
        try:   
            target_name, target_extension = os.path.splitext(os.path.basename(target))
            if target_extension == '.py':
                result = subprocess.run(["python", target], input=self.generate().encode(), capture_output=True, timeout=1)
            else:
                result = subprocess.run([target], input=self.generate().encode(), capture_output=True, timeout=1)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print("Process timed out")
            return -1, b'', b'Timeout'
        
    def fuzz(self):
        
        for i in range (self.num_iterations):
            if i % 100 == 0:
                print(f"Progress: {i+1}/{self.num_iterations}")
            retcode, stdout, stderr = self.run(self.target)
            if retcode != 0:
                print(f"Crash detected! Return code: {retcode}")
                print(f"Stdout: {stdout.decode()}")
                print(f"Stderr: {stderr.decode()}")

                self.crashes.append((retcode, stdout, stderr))
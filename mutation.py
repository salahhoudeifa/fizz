import random
import string
import os
import subprocess
import time
from pathlib import Path

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeRemainingColumn   
)

prog = Progress(
    TextColumn("[progress.description]{task.description}"),
    ">",
    BarColumn(),
    ">",
    TimeRemainingColumn()
)

# Mutation-based fuzz (WIP)

corpus_path = Path.cwd() / 'corpus'
corpus_seed = set()
if corpus_path.exists() and corpus_path.is_dir():
    for file in os.listdir(corpus_path):
        file_path = corpus_path / file
        if file_path.is_file():
            with open(file_path, 'r', errors='ignore') as f:
                corpus_seed.add(f.read())

class Mutation():
    def __init__(self, target, num_iterations, crashes):
        self.target = target
        self.num_iterations = num_iterations
        self.crashes = []

    def mutate(self, input_data):
        if not input_data:
            input_data = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 32)))
        
        input_bytes = bytearray(input_data.encode())
        
        mutation_type = random.choice(['bit_flip', 'byte_add', 'byte_remove', 'byte_modify'])

        if mutation_type == 'bit_flip':
            index = random.randint(0, len(input_bytes) - 1)
            bit = 1 << random.randint(0, 7)              
            input_bytes[index] ^= bit

        elif mutation_type == 'byte_add':
            index = random.randint(0, len(input_bytes))
            byte = random.randint(0, 255)
            input_bytes.insert(index, byte)

        elif mutation_type == 'byte_remove' and len(input_bytes) > 0:
            index = random.randint(0, len(input_bytes) - 1)
            del input_bytes[index]

        elif mutation_type == 'byte_modify':
            index = random.randint(0, len(input_bytes) - 1)
            byte = random.randint(0, 255)
            input_bytes[index] = byte

        return input_bytes.decode(errors='ignore')

    def run(self, target, task_id):
        try:   
            target_name, target_extension = os.path.splitext(os.path.basename(target))
            for i in range(self.num_iterations):
                input_data = random.choice(list(corpus_seed)) if corpus_seed else None
                mutated_input = self.mutate(input_data)
                if target_extension == '.py':
                    result = subprocess.run(["python", target], input=mutated_input.encode(), capture_output=True, timeout=1)  
                    prog.update(task_id=task_id, advance=1)  
                else:
                    result = subprocess.run([target], input=mutated_input.encode(), capture_output=True, timeout=1)
                    prog.update(task_id=task_id, advance=1)   
        except subprocess.TimeoutExpired:
            print("Process timed out")
            return -1, b'', b'Timeout', None
        
    def fuzz(self):
        log_file = open(f"log_{time.strftime('%Y%m%d-%H%M%S')}.txt", "w")
        with prog:
            task = prog.add_task("Fuzzing in progress...", total=self.num_iterations)
            for i in range (self.num_iterations):
                retcode, stdout, stderr, finput = self.run(self.target, task)
                if retcode != 0:
                  if (retcode, stdout, stderr) not in self.unique_crashes:
                    self.unique_crashes.add((retcode, stdout, stderr))
                    log_file.write(f"Return code: {retcode}\n")
                    log_file.write(f"Stdout: {stdout.decode()}\n")
                    log_file.write(f"Stderr: {stderr.decode()}\n")
                    log_file.write("============================\n")
                self.crashes.append((retcode, stdout, stderr, finput))
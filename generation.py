import random
import string
import subprocess
import os
from pathlib import Path
import time

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

# Generation-based fuzz

class Fuzzer:
    def __init__(self, target, num_iterations, crashes):
        self.target = target
        self.num_iterations = num_iterations
        self.crashes = []
        self.unique_crashes = set()
        self.unique_inputs = set()

    def generate(self):
        length = random.randint(1, 32)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def run(self, target, task_id):
        try:   
            target_name, target_extension = os.path.splitext(os.path.basename(target))
            generated_input = self.generate()
            if target_extension == '.py':
                result = subprocess.run(["python", target], input=generated_input.encode(), capture_output=True, timeout=1)
                prog.update(task_id=task_id, advance=1)
            else:
                result = subprocess.run([target], input=generated_input().encode(), capture_output=True, timeout=1)
                prog.update(task_id=task_id, advance=1)
                if task_id.finished:
                    print("Fuzzing complete.")
            return result.returncode, result.stdout, result.stderr, generated_input
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
                      self.unique_crashes.add(stderr)    
                      log_file.write(f"Crash detected! Return code: {retcode}\n")
                      log_file.write(f"Stdout: {stdout.decode()}\n")
                      log_file.write(f"Stderr: {stderr.decode()}\n")
                      log_file.write("============================\n")
                  self.crashes.append((retcode, stdout, stderr, finput))   
                else: # Store valid inputs for later use
                    corpus_dir = Path.cwd() / 'corpus'
                    if not corpus_dir.exists():
                        corpus_dir.mkdir()
                    if finput not in self.unique_inputs:
                        self.unique_inputs.add(finput)
                    with open(f"corpus/input_{i}.txt", "w") as f:
                        f.write(finput)
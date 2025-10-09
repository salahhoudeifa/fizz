import random
import string
import os
import subprocess

# Mutation-based fuzz (WIP)

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

    def run(self, target, input_data):
        try:   
            target_name, target_extension = os.path.splitext(os.path.basename(target))
            for i in range(self.num_iterations):
                mutated_input = self.mutate(input_data)
                if target_extension == '.py':
                    result = subprocess.run(["python", target], input=mutated_input.encode(), capture_output=True, timeout=1)
                else:
                    result = subprocess.run([target], input=mutated_input.encode(), capture_output=True, timeout=1)
                if result.returncode != 0:
                    print(f"Crash detected! Return code: {result.returncode}")
                    print(f"Stdout: {result.stdout.decode()}")
                    print(f"Stderr: {result.stderr.decode()}")
                    self.crashes.append((result.returncode, result.stdout, result.stderr, mutated_input))
        except subprocess.TimeoutExpired:
            print("Process timed out")
            return -1, b'', b'Timeout', None
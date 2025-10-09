import os
import typer
import generation
import mutation
import time
import pyfiglet
import random
from pathlib import Path
from colorama import Fore, Style

app = typer.Typer(help="a simple fuzz testing tool")


@app.command("generate")
def generatefuzz(target: str = typer.Argument(..., help="The target binary to fuzz"),
        num_iterations: int = typer.Option(1000, help="Number of fuzzing iterations")):
    """
    Fuzz a target binary using generation-based inputs.
    """
    Fuzzer = generation.Fuzzer(target, num_iterations, [])
    Fuzzer.fuzz()
    start__time = time.time()
    if Fuzzer.crashes:
        print(f"Total crashes found: {len(Fuzzer.crashes)}")
    else:
        print("No crashes found.")
    end_time = time.time()
    print("Time elapsed:", end_time - start__time, "seconds")    

@app.command("mutate")
def mutatefuzz(target: str = typer.Argument(..., help="The target binary to fuzz"),
        num_iterations: int = typer.Option(1000, help="Number of fuzzing iterations")):
    """
    Placeholder for mutation-based fuzzing.
    """
    Mutator = mutation.Mutation(target, num_iterations, [])
    corpus_seed = set()
    corpus_path = Path(__file__).resolve().parent / 'corpus'

    for file in os.listdir(corpus_path):
        if os.path.isfile(os.path.join(corpus_path, file)):
            corpus_seed.add(file)


    start_time = time.time()
    for seed in corpus_seed:
        try:
            with open(os.path.join(corpus_path, seed), 'r') as f:
                corpus_seed.add(f.read())
                Mutator.run(target, f.read())
        except IOError:
            print(f"Could not read file: {seed}")

    if Mutator.crashes:
        print(f"Total crashes found: {len(Mutator.crashes)}")
    else:
        print("No crashes found.")
    end_time = time.time()
    print("Time elapsed:", end_time - start_time, "seconds")         

@app.command("api")
def apifuzz():
    """
    Placeholder for API fuzzing.
    """
    print("API fuzzing is not yet implemented.")

@app.command("clear")
def clear_corpus():
    """
    Clear the corpus directory.
    """
    corpus_path = Path(__file__).resolve().parent / 'corpus'
    if corpus_path.exists() and corpus_path.is_dir():
        for file in os.listdir(corpus_path):
            file_path = corpus_path / file
            try:
                if file_path.is_file():
                    file_path.unlink()
            except Exception as e:
                print(f"Error deleting file {file}: {e}")
        print("Corpus directory cleared.")
    else:
        print("Corpus directory does not exist.")    

if __name__ == "__main__":
    ascii_banner = pyfiglet.figlet_format("fizz", font="larry3d")
    print(Fore.RED + ascii_banner + Style.NORMAL + "\n" + Fore.WHITE + "\n" + "==============================\n")
    app()
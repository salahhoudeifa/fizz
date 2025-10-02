import typer
import dumbfuzz
import time

app = typer.Typer()

@app.command()
def fuzz(target: str = typer.Argument(..., help="The target binary to fuzz"),
        num_iterations: int = typer.Option(1000, help="Number of fuzzing iterations")):
    Fuzzer = dumbfuzz.Fuzzer(target, num_iterations, [])
    Fuzzer.fuzz()
    start__time = time.time()
    if Fuzzer.crashes:
        print(f"Total crashes found: {len(Fuzzer.crashes)}")
    else:
        print("No crashes found.")
    end_time = time.time()
    print("Time elapsed:", end_time - start__time, "seconds")    


if __name__ == "__main__":
    app()
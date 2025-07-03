import numpy as np
import csv
import sys  # コマンドライン引数を扱うためにインポート
from qiskit_optimization.applications import Tsp
from qiskit_optimization.translators import from_docplex_mp
# --- 修正点: Qiskit 1.0以降の正しいインポートパスに変更 ---
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
# ----------------------------------------------------
from qiskit.primitives import Sampler
from qiskit.utils import algorithm_globals

def read_cities_from_csv(filename):
    """Reads city coordinates from the specified CSV file."""
    cities = []
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header 'x,y'
        for row in reader:
            cities.append((float(row[0]), float(row[1])))
    return cities

def calculate_distance_matrix(cities):
    """Calculates the Euclidean distance between each pair of cities."""
    num_cities = len(cities)
    dist_matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(i, num_cities):
            if i == j:
                continue
            dist = np.sqrt((cities[i][0] - cities[j][0])**2 +
                           (cities[i][1] - cities[j][1])**2)
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix

def write_solution_to_csv(filename, path):
    """Writes the solution path to the specified output CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index'])
        for city_index in path:
            writer.writerow([city_index])
    print(f"\nSolution successfully written to '{filename}'")

def solve_tsp_with_qaoa(dist_matrix):
    """
    Solves the TSP using the QAOA algorithm on a local simulator.

    Args:
        dist_matrix (np.ndarray): A matrix of distances between cities.

    Returns:
        list: The optimal path found by the algorithm.
    """
    # Create a TSP instance from the distance matrix
    tsp_problem = Tsp(dist_matrix)

    # Convert the TSP problem into a Quadratic Unconstrained Binary
    # Optimization (QUBO) problem, which quantum computers can understand.
    qp = from_docplex_mp(tsp_problem.to_docplex())

    # --- Set up the QAOA Algorithm ---
    # We need two main components:
    # 1. A classical optimizer to tune the quantum circuit's parameters.
    # 2. A quantum backend (a simulator in this case) to run the circuit.

    # 1. Classical Optimizer (COBYLA is a good choice for noisy environments)
    optimizer = COBYLA()

    # 2. Quantum Backend (Sampler uses a local simulator by default)
    # This simulates the quantum computation without needing a real quantum device.
    sampler = Sampler()

    # Seed for reproducibility
    algorithm_globals.random_seed = 12345

    # Initialize the QAOA algorithm
    # 'reps' is the depth of the quantum circuit. A higher number can lead
    # to better results but takes longer to run.
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)

    # Run the algorithm to find the minimum eigenvalue of the problem.
    # This corresponds to the shortest path length.
    print("Running QAOA on the simulator... (This may take a few minutes)")
    result = qaoa.compute_minimum_eigenvalue(qp.to_ising()[0])

    # Interpret the result to get the path
    optimal_path = tsp_problem.interpret(result)

    print("\n--- Quantum Algorithm Finished ---")
    print(f"Optimal path found: {optimal_path}")
    print(f"Total distance: {tsp_problem.tsp_value(optimal_path, dist_matrix):.4f}")
    
    return optimal_path

def main():
    """Main function to run the TSP solver."""
    
    # --- Configuration ---
    # コマンドラインから入力ファイル名を取得
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # 引数がなければ使い方を表示し、デフォルトでChallenge 0を解く
        print("Usage: python your_script_name.py <input_filename>")
        print("No input file provided. Defaulting to 'input_0.csv'.")
        input_filename = 'input_0.csv'

    # 入力ファイル名から出力ファイル名を自動生成
    # 例: 'input_0.csv' -> 'output_0.csv'
    output_filename = input_filename.replace('input_', 'output_')

    try:
        # Step 1: Read city data from the input file
        print(f"Reading city data from '{input_filename}'...")
        cities = read_cities_from_csv(input_filename)
        num_cities = len(cities)
        print(f"Found {num_cities} cities.")

        # Step 2: Calculate the distance matrix
        print("Calculating distance matrix...")
        dist_matrix = calculate_distance_matrix(cities)

        # Step 3: Solve the TSP using the quantum algorithm
        optimal_path = solve_tsp_with_qaoa(dist_matrix)

        # Step 4: Write the solution to the output file
        write_solution_to_csv(output_filename, optimal_path)

    except FileNotFoundError:
        print(f"ERROR: Input file not found: '{input_filename}'")
        print("Please make sure you have cloned the 'google-step-tsp' repository")
        print("and are running this script from the same directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

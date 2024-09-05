import pandas as pd
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.visualization import plot_histogram
from math import pi
from qiskit.providers.aer import Aer

import time

# Load your new CSV file
file_path = 'chicago_crime.csv'  # Replace 'new_file.csv' with the actual file name
df = pd.read_csv(file_path)

# Define the oracle based on the search key
def mark_state(circuit, qr_target, qr_auxiliary, n, search_key):
    for qubit, bit in enumerate(search_key):
        if bit == '1':
            circuit.x(qr_target[qubit])
    for qubit in range(n):
        circuit.cx(qr_target[qubit], qr_auxiliary[qubit])
    for qubit, bit in enumerate(search_key):
        if bit == '1':
            circuit.x(qr_target[qubit])

# Define Grover's diffusion operator
def diffusion(circuit, qr, n):
    circuit.h(qr)
    circuit.x(qr)
    circuit.h(qr[n-1])
    circuit.mcx(qr[:-1], qr[n-1])  # multi-controlled-x
    circuit.h(qr)
    circuit.x(qr)
    circuit.h(qr[n-1])

# Grover's search algorithm
def grover_search(search_column, search_value):
    start_time = time.time()
    n = 10  # Reduced the number of qubits for simplicity

    # Print available column names for verification
    print("Available column names:", df.columns)

    # Check if the specified column exists (case-insensitive)
    search_column_lower = search_column.lower()
    matching_columns = [col for col in df.columns if col.lower() == search_column_lower]

    if not matching_columns:
        print(f"Column '{search_column}' not found in the DataFrame.")
        return

    # Convert the entire column to lowercase for case-insensitive search
    df_lower = df.applymap(lambda x: x.lower() if type(x) == str else x)

    # Find the index corresponding to the search key
    search_value_str = str(search_value)
    index = df_lower[df_lower[matching_columns[0]] == search_value_str.lower()].index

    if index.empty:
        print(f"'{search_value_str}' not found in column '{search_column}'.")
        return

    search_value_binary = format(index[0], '010b')  # Convert index to 10-bit binary representation

    qr_target = QuantumRegister(n, 'target')  # Quantum register for the target
    qr_auxiliary = QuantumRegister(n, 'auxiliary')  # Quantum register for the auxiliary
    cr = ClassicalRegister(n, 'result')  # Classical register to measure the result
    qc = QuantumCircuit(qr_target, qr_auxiliary, cr)

    # Apply Hadamard gates to all qubits
    qc.h(qr_target)

    iterations = int((pi/4) * (2**((n-1)/2)))  # Number of Grover iterations

    for _ in range(iterations):
        mark_state(qc, qr_target, qr_auxiliary, n, search_value_binary)
        diffusion(qc, qr_target, n)

    # Measure qubits
    qc.measure(qr_target, cr)

    # Execute the quantum circuit
    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(transpile(qc, backend, optimization_level=0))  # Set optimization level to 0
    result = job.result()

    # Get the measurement outcome
    counts = result.get_counts()

    print("Counts:", counts)  # Print counts for debugging

    # Check if the search key is in the counts
    if search_value_binary in counts:
        # Print the whole row (case-sensitive)
        print(f"\nRow containing '{search_value_str}' in column '{search_column}':\n{df.iloc[index[0]]}")
    else:
        print(f"'{search_value_str}' not found in column '{search_column}'.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Runtime: {elapsed_time} seconds")

# Example usage:
search_column = input("Enter the column name to search: ")
search_value = input(f"Enter the value in column '{search_column}' to search: ")



grover_search(search_column, search_value)
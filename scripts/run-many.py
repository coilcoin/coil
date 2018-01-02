#!/usr/bin/env python3

# run-many [num_of_nodes] [starting_port]
# Part of the Coil Project
# Written by Jesse Sibley

import sys
import subprocess

def run_many(args):
    num_of_nodes = 5
    starting_port = 8080

    if len(args) > 1:
        num_of_nodes = int(args[1])

    if len(args) == 2:
        starting_port = int(args[2])

    for i in range(0, num_of_nodes):
        port = str(starting_port + i)
        print(f"Initializing node {i} on port {port}")
        subprocess.call("python", ["coil.py", port])

if __name__ == "__main__":
    run_many(sys.argv[1:])

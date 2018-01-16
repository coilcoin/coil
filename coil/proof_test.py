import hashlib
import os

def doubleHash(input):
    return hashlib.sha256(hashlib.sha256(input).digest()).hexdigest()

def doubleHashEncode(input):
    return doubleHash(input.encode("utf8"))

# Working out an appropriate target

runs = 10000000
results = []
mean = 0

for i in range(0, runs):
    message = str(os.urandom(20))

    result = doubleHashEncode(message)
    result = int(result, 16)

    results.append(result)

# SORT RESULTS
results = sorted(results)

print(len(results))
mean = sum(results) / len(results)
largest = max(results)
minimum = min(results)

lq = results[int(0.25 * len(results))]
uq = results[int(0.75 * len(results))]

target = minimum

print("Iterations", runs)
print("Mean", mean)
print("Largest", largest)
print("Minimum", minimum)

print("Lower Quartile", lq)
print("Upper Quartile", uq)
print(lq < uq)

print("Calculated target", target)
# Benchmarks

This directory contains pytest-based benchmarks for the rbloom library.

## Installation

To run the benchmarks, you need to install pytest-benchmark:

```bash
pip install pytest-benchmark
```

## Running Benchmarks

### Per-Operation Benchmarks

Run individual operation benchmarks (add, update, membership check):

```bash
pytest benchmarks/test_per_operation.py --benchmark-only
```

### Comparison Benchmarks

Compare rbloom against other bloom filter implementations. First, install the optional dependencies:

```bash
pip install -r benchmarks/requirements.txt
```

Then run the comparison benchmarks:

```bash
pytest benchmarks/test_compare.py --benchmark-only
```

Note: The comparison benchmarks will only run for libraries that are installed. If you don't install the optional dependencies, only the rbloom benchmark will run.

## Options

- `--benchmark-only`: Only run benchmarks (skip regular tests)
- `--benchmark-disable-gc`: Disable garbage collection during benchmarks for more consistent results
- `--benchmark-save=NAME`: Save benchmark results to a file
- `--benchmark-compare`: Compare against previously saved results
- `--benchmark-autosave`: Automatically save results after each run

For example:

```bash
# Save benchmark results
pytest benchmarks/test_per_operation.py --benchmark-only --benchmark-save=baseline

# Compare against saved results
pytest benchmarks/test_per_operation.py --benchmark-only --benchmark-compare=baseline
```

## Benchmark Details

### test_per_operation.py

- `test_benchmark_add_element`: Measures time to add a single element
- `test_benchmark_update_batch_list`: Measures time to add elements from a list
- `test_benchmark_update_batch_generator`: Measures time to add elements from a generator
- `test_benchmark_membership_check`: Measures time to check if an element exists

### test_compare.py

- `test_benchmark_comparison`: Compares rbloom against other bloom filter libraries
  - rbloom
  - pybloomfiltermmap3
  - pybloom3
  - flor
  - bloomfilter2

## Legacy Scripts

The original benchmark scripts (`per_operation.py` and `compare.py`) are still available but have been superseded by the pytest versions (`test_per_operation.py` and `test_compare.py`).

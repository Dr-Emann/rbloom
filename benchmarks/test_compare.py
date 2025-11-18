import struct
import pytest

# Import bloom filter libraries with error handling for optional dependencies
try:
    import rbloom
    has_rbloom = True
except ImportError:
    has_rbloom = False

try:
    import pybloomfilter
    has_pybloomfilter = True
except ImportError:
    has_pybloomfilter = False

try:
    import pybloom
    has_pybloom = True
except ImportError:
    has_pybloom = False

try:
    import flor
    has_flor = True
except ImportError:
    has_flor = False

try:
    import bloom_filter2
    has_bloom_filter2 = True
except ImportError:
    has_bloom_filter2 = False


NUM_ITEMS = 10_000_000


def run_benchmark_floats(bloom_class):
    """Benchmark adding and checking floats"""
    bf = bloom_class(NUM_ITEMS, 0.01)

    for i in range(NUM_ITEMS):
        bf.add(i + 0.5)  # floats because ints are hashed as themselves

    for i in range(NUM_ITEMS):
        if i + 0.5 not in bf:
            raise ValueError("Should be no false negatives")


def run_benchmark_bytes(bloom_class):
    """Benchmark adding and checking bytes (for libraries that don't support floats)"""
    bf = bloom_class(NUM_ITEMS, 0.01)

    for i in range(NUM_ITEMS):
        bf.add(struct.pack("d", i + 0.5))

    for i in range(NUM_ITEMS):
        if struct.pack("d", i + 0.5) not in bf:
            raise ValueError("Should be no false negatives")


# Build the list of bloom filter implementations to test
bloom_filters = []

if has_rbloom:
    bloom_filters.append(("rbloom", rbloom.Bloom, "floats"))

if has_pybloomfilter:
    bloom_filters.append(("pybloomfiltermmap3", pybloomfilter.BloomFilter, "bytes"))

if has_pybloom:
    bloom_filters.append(("pybloom3", pybloom.BloomFilter, "floats"))

if has_flor:
    bloom_filters.append(("flor", flor.BloomFilter, "floats"))

if has_bloom_filter2:
    bloom_filters.append(("bloomfilter2", bloom_filter2.BloomFilter, "floats"))


@pytest.mark.parametrize("name,bloom_class,data_type", bloom_filters)
def test_benchmark_comparison(benchmark, name, bloom_class, data_type):
    """Benchmark comparison of different bloom filter implementations"""
    if data_type == "floats":
        benchmark(run_benchmark_floats, bloom_class)
    else:
        benchmark(run_benchmark_bytes, bloom_class)

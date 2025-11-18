import pytest
from rbloom import Bloom

NUMBER = 1000000


@pytest.fixture
def bloom():
    """Fixture providing a fresh bloom filter for each test"""
    return Bloom(NUMBER, 0.01)


@pytest.fixture
def populated_bloom():
    """Fixture providing a bloom filter with one stored object"""
    b = Bloom(NUMBER, 0.01)
    stored_obj = object()
    b.add(stored_obj)
    # Also add many other objects to make it realistic
    b.update(object() for _ in range(NUMBER))
    return b, stored_obj


@pytest.fixture
def objects_list():
    """Fixture providing a list of objects to add"""
    return [object() for _ in range(NUMBER)]


def test_benchmark_add_element(benchmark, bloom):
    """Benchmark time to insert a single element"""
    obj = object()
    benchmark(bloom.add, obj)


def test_benchmark_update_batch_list(benchmark, bloom, objects_list):
    """Benchmark time to insert elements in a batch from a list"""
    benchmark(bloom.update, objects_list)


def test_benchmark_update_batch_generator(benchmark, bloom):
    """Benchmark time to insert elements in a batch via a generator"""
    def update_from_generator():
        bloom.update(object() for _ in range(NUMBER))

    benchmark(update_from_generator)


def test_benchmark_membership_check(benchmark, populated_bloom):
    """Benchmark time to check if an object is present"""
    bloom, stored_obj = populated_bloom
    benchmark(lambda: stored_obj in bloom)

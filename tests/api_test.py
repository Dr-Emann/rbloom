import gc
import weakref
import pytest

from rbloom import Bloom
from hashlib import sha256
from pickle import dumps
import os


def sha_based(obj):
    h = sha256(dumps(obj)).digest()
    return int.from_bytes(h[:16], "big") - 2**127


def test_bloom_basic_operations(bloom: Bloom):
    """Test basic bloom filter operations"""
    assert not bloom
    assert bloom.approx_items == 0.0

    bloom.add('foo')
    assert bloom
    assert bloom.approx_items > 0.0

    bloom.add('bar')

    assert 'foo' in bloom
    assert 'bar' in bloom
    assert 'baz' not in bloom

    bloom.update(['baz', 'qux'])
    assert 'baz' in bloom
    assert 'qux' in bloom


def test_bloom_copy_and_clear(bloom: Bloom):
    """Test bloom filter copy and clear operations"""
    bloom.update(['foo', 'bar', 'baz', 'qux'])

    other = bloom.copy()
    assert other == bloom
    assert other is not bloom

    other.clear()
    assert not other
    assert other.approx_items == 0.0

    other.update(['foo', 'bar', 'baz', 'qux'])
    assert other == bloom


def test_bloom_set_operations(bloom: Bloom):
    """Test bloom filter set operations (union, intersection, etc.)"""
    bloom.update(['foo', 'bar', 'baz', 'qux'])

    other = bloom.copy()
    other.update(str(i).encode()*500 for i in range(100000))
    for i in range(100000):
        assert str(i).encode()*500 in other
    assert bloom != other
    assert bloom & other == bloom
    assert bloom | other == other

    bloom &= other
    assert bloom < other


def test_bloom_comparison_operations(bloom: Bloom):
    """Test bloom filter comparison operations"""
    bloom.update(['foo', 'bar', 'baz', 'qux'])

    other = bloom.copy()
    other.update(str(i).encode()*500 for i in range(100000))
    bloom &= other

    orig = bloom.copy()
    bloom |= other
    assert bloom == other
    assert bloom > orig
    assert bloom >= orig
    assert bloom.issuperset(other)
    assert orig <= bloom
    assert orig.issubset(bloom)
    assert bloom >= bloom
    assert bloom.issuperset(bloom)
    assert bloom <= bloom
    assert bloom.issubset(bloom)


def test_bloom_update_and_union(bloom: Bloom):
    """Test bloom filter update and union operations"""
    bloom.update(['foo', 'bar', 'baz', 'qux'])

    other = bloom.copy()
    other.update(str(i).encode()*500 for i in range(100000))
    bloom &= other
    orig = bloom.copy()

    bloom = orig.copy()
    bloom.update(other)
    assert bloom == other
    assert bloom > orig

    bloom = orig.copy()
    assert other == bloom.union(other)
    assert bloom == bloom.intersection(other)

    bloom.intersection_update(other)
    assert bloom == orig


def test_bloom_persistence(bloom: Bloom):
    """Test bloom filter persistence to file and bytes"""
    bloom.update(['foo', 'bar', 'baz', 'qux'])

    # TEST PERSISTENCE
    if not bloom.hash_func is hash:
        # find a filename that doesn't exist
        i = 0
        while os.path.exists(f'UNIT_TEST_{i}.bloom'):
            i += 1
        filename = f'test{i}.bloom'

        try:
            # save and load
            bloom.save(filename)
            bloom2 = Bloom.load(filename, bloom.hash_func)
            assert bloom == bloom2
        finally:
            # remove the file
            os.remove(filename)

        # TEST bytes PERSISTENCE
        bloom_bytes = bloom.save_bytes()
        assert type(bloom_bytes) == bytes
        bloom3 = Bloom.load_bytes(bloom_bytes, bloom.hash_func)
        assert bloom == bloom3


def test_circular_ref():
    """Test that circular references are properly garbage collected"""
    def loop_hash_func(x):
        return sha_based(x)
    weak_ref = weakref.ref(loop_hash_func)
    bloom = Bloom(1000, 0.1, hash_func=loop_hash_func)
    assert gc.get_referents(bloom) == [loop_hash_func]
    loop_hash_func.bloom = bloom
    del bloom
    del loop_hash_func
    gc.collect()
    assert weak_ref() is None


def test_operations_with_self():
    """Test bloom filter operations with itself"""
    bloom = Bloom(1000, 0.1)
    bloom.add('foo')
    assert 'foo' in bloom
    bloom |= bloom
    bloom &= bloom
    bloom.update(bloom)
    bloom.update(bloom, bloom)
    bloom.update(bloom, ['bob'], bloom)
    assert 'foo' in bloom
    assert 'bob' in bloom

    bloom.intersection_update(bloom)
    bloom.intersection_update(bloom, bloom)
    bloom.intersection_update(bloom, ['foo'], bloom)
    assert 'foo' in bloom
    assert 'bob' not in bloom
    assert bloom == bloom
    assert bloom <= bloom
    assert bloom >= bloom
    assert not (bloom > bloom)
    assert not (bloom < bloom)
    assert bloom.issubset(bloom)
    assert bloom.issuperset(bloom)
    assert bloom.union(bloom) == bloom
    assert bloom.union(bloom, bloom) == bloom
    assert bloom.intersection(bloom) == bloom
    assert bloom.intersection(bloom, bloom) == bloom


def test_bloom_repr():
    """Test bloom filter string representation"""
    assert repr(Bloom(27_000, 0.0317)) == "<Bloom size_in_bits=193960 approx_items=0.0>"


def test_bloom_hash_func():
    """Test bloom filter hash function property"""
    assert Bloom(1140, 0.999).hash_func == hash
    assert Bloom(102, 0.01, hash_func=hash).hash_func is hash
    assert Bloom(103100, 0.51, hash_func=sha_based).hash_func is sha_based


@pytest.fixture(params=[
    (13242, 0.0000001, None),
    (9874124, 0.01, sha_based),
    (2837, 0.5, hash),
])
def bloom(request):
    """Fixture that provides bloom filters with different configurations"""
    size, error_rate, hash_func = request.param
    if hash_func is None:
        return Bloom(size, error_rate)
    return Bloom(size, error_rate, hash_func=hash_func)

"""
Advanced Python Concepts Tutorial
=================================

Covers decorators, context managers, generators, descriptors,
metaclasses, and other advanced Python features.

Key concepts:
- Decorators (function and class)
- Context managers
- Generators and iterators
- Descriptors
- Metaclasses
- __slots__
"""

import functools
import time
import contextlib
from typing import Generator, Any

# =============================================================================
# 1. Decorators - Function Wrappers
# =============================================================================

def timer(func):
    """
    Basic decorator - measures execution time.
    Wraps function to add timing logic.
    """
    @functools.wraps(func)  # Preserve function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator with arguments.
    Retries function on failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def cache(func):
    """
    Simple memoization decorator.
    Caches results based on arguments.
    """
    _cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in _cache:
            _cache[args] = func(*args)
        return _cache[args]

    wrapper.cache = _cache  # Expose cache for inspection
    return wrapper


def demo_decorators():
    """Demonstrate decorator usage."""
    print("=" * 60)
    print("1. DECORATORS")
    print("=" * 60)

    @timer
    def slow_function():
        time.sleep(0.1)
        return "done"

    result = slow_function()
    print(f"Result: {result}\n")

    # Decorator with arguments
    attempt_count = 0

    @retry(max_attempts=3, delay=0.1)
    def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("Not yet!")
        return "success"

    result = flaky_function()
    print(f"Result after retries: {result}\n")

    # Memoization
    @cache
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    start = time.time()
    result = fibonacci(30)
    elapsed = time.time() - start
    print(f"fibonacci(30) = {result} ({elapsed:.4f}s)")
    print(f"Cache entries: {len(fibonacci.cache)}")

    print("-" * 60)


# =============================================================================
# 2. Class Decorators
# =============================================================================

def singleton(cls):
    """
    Class decorator - ensures single instance.
    """
    instances = {}

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def auto_repr(cls):
    """
    Class decorator - auto-generates __repr__.
    """
    def __repr__(self):
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
        )
        return f"{cls.__name__}({attrs})"

    cls.__repr__ = __repr__
    return cls


def demo_class_decorators():
    """Demonstrate class decorators."""
    print("\n" + "=" * 60)
    print("2. CLASS DECORATORS")
    print("=" * 60)

    @singleton
    class Database:
        def __init__(self, url):
            self.url = url
            print(f"Connecting to {url}")

    db1 = Database("postgres://localhost")
    db2 = Database("mysql://localhost")  # Won't create new instance

    print(f"Same instance? {db1 is db2}")
    print(f"URL: {db1.url}\n")

    @auto_repr
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p = Point(3, 4)
    print(f"Auto-generated repr: {p}")

    print("-" * 60)


# =============================================================================
# 3. Context Managers
# =============================================================================

class FileManager:
    """
    Context manager using __enter__ and __exit__.
    Ensures cleanup even on exceptions.
    """

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()
        # Return True to suppress exceptions
        return False


@contextlib.contextmanager
def timer_context(name: str):
    """
    Context manager using generator.
    Simpler than class-based approach.
    """
    start = time.time()
    print(f"Starting {name}")
    try:
        yield  # Code in 'with' block runs here
    finally:
        elapsed = time.time() - start
        print(f"{name} took {elapsed:.4f}s")


@contextlib.contextmanager
def temporary_change(obj, attr, value):
    """
    Temporarily change an attribute.
    Restores original value on exit.
    """
    original = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, original)


def demo_context_managers():
    """Demonstrate context managers."""
    print("\n" + "=" * 60)
    print("3. CONTEXT MANAGERS")
    print("=" * 60)

    # Class-based
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_path = f.name
        f.write("test")

    with FileManager(temp_path, 'r') as f:
        content = f.read()
        print(f"Content: {content}\n")

    os.unlink(temp_path)

    # Generator-based
    with timer_context("sleep"):
        time.sleep(0.1)

    print()

    # Temporary change
    class Config:
        debug = False

    config = Config()
    print(f"Before: debug={config.debug}")

    with temporary_change(config, 'debug', True):
        print(f"Inside: debug={config.debug}")

    print(f"After: debug={config.debug}")

    print("-" * 60)


# =============================================================================
# 4. Generators and Iterators
# =============================================================================

def fibonacci_generator(limit: int) -> Generator[int, None, None]:
    """
    Generator function - yields values lazily.
    Memory efficient for large sequences.
    """
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


def infinite_counter(start: int = 0) -> Generator[int, None, None]:
    """Infinite generator."""
    n = start
    while True:
        yield n
        n += 1


class Range:
    """
    Custom iterator class.
    Implements iterator protocol.
    """

    def __init__(self, start, stop, step=1):
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


def demo_generators():
    """Demonstrate generators and iterators."""
    print("\n" + "=" * 60)
    print("4. GENERATORS AND ITERATORS")
    print("=" * 60)

    # Generator function
    print("Fibonacci generator:")
    for num in fibonacci_generator(10):
        print(num, end=" ")
    print("\n")

    # Generator expression
    squares = (x**2 for x in range(5))
    print(f"Generator expression: {list(squares)}\n")

    # Infinite generator with islice
    from itertools import islice
    counter = infinite_counter(100)
    first_5 = list(islice(counter, 5))
    print(f"Infinite counter (first 5): {first_5}\n")

    # Custom iterator
    custom_range = Range(0, 5)
    print(f"Custom Range: {list(custom_range)}")

    print("-" * 60)


# =============================================================================
# 5. Generator Send and Throw
# =============================================================================

def coroutine_example():
    """
    Generator as coroutine.
    Can receive values via send().
    """
    print("Coroutine started")
    total = 0
    try:
        while True:
            value = yield total
            if value is None:
                break
            print(f"Received: {value}")
            total += value
    except GeneratorExit:
        print("Coroutine closed")


def demo_generator_coroutine():
    """Demonstrate generator as coroutine."""
    print("\n" + "=" * 60)
    print("5. GENERATOR COROUTINES (send/throw)")
    print("=" * 60)

    coro = coroutine_example()
    next(coro)  # Initialize

    print(f"Total: {coro.send(10)}")
    print(f"Total: {coro.send(20)}")
    print(f"Total: {coro.send(30)}")

    coro.close()

    print("-" * 60)


# =============================================================================
# 6. Descriptors
# =============================================================================

class Validator:
    """
    Descriptor for validated attributes.
    Controls attribute access.
    """

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")
        setattr(obj, self.private_name, value)


class Lazy:
    """
    Lazy evaluation descriptor.
    Computes value once, caches result.
    """

    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.name, value)  # Replace descriptor
        return value


def demo_descriptors():
    """Demonstrate descriptors."""
    print("\n" + "=" * 60)
    print("6. DESCRIPTORS")
    print("=" * 60)

    class Product:
        price = Validator(min_value=0, max_value=10000)
        quantity = Validator(min_value=0)

        def __init__(self, name, price, quantity):
            self.name = name
            self.price = price
            self.quantity = quantity

    p = Product("Widget", 100, 5)
    print(f"Product: {p.name}, ${p.price}, qty: {p.quantity}")

    try:
        p.price = -10
    except ValueError as e:
        print(f"Validation error: {e}")

    # Lazy descriptor
    class DataProcessor:
        def __init__(self, data):
            self.data = data

        @Lazy
        def processed(self):
            print("  Processing data (expensive)...")
            return [x * 2 for x in self.data]

    print("\nLazy evaluation:")
    dp = DataProcessor([1, 2, 3])
    print("First access:")
    print(f"  Result: {dp.processed}")
    print("Second access (cached):")
    print(f"  Result: {dp.processed}")

    print("-" * 60)


# =============================================================================
# 7. Metaclasses
# =============================================================================

class SingletonMeta(type):
    """
    Metaclass for singleton pattern.
    Controls class creation.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RegistryMeta(type):
    """
    Metaclass that registers all subclasses.
    """
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # Don't register base class
            mcs.registry[name] = cls
        return cls


def demo_metaclasses():
    """Demonstrate metaclasses."""
    print("\n" + "=" * 60)
    print("7. METACLASSES")
    print("=" * 60)

    class Config(metaclass=SingletonMeta):
        def __init__(self):
            print("Config initialized")

    c1 = Config()
    c2 = Config()
    print(f"Same instance? {c1 is c2}\n")

    # Registry metaclass
    class Plugin(metaclass=RegistryMeta):
        pass

    class PDFPlugin(Plugin):
        pass

    class CSVPlugin(Plugin):
        pass

    print(f"Registered plugins: {list(RegistryMeta.registry.keys())}")

    print("-" * 60)


# =============================================================================
# 8. __slots__ - Memory Optimization
# =============================================================================

class WithoutSlots:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WithSlots:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y


def demo_slots():
    """Demonstrate __slots__ memory optimization."""
    print("\n" + "=" * 60)
    print("8. __slots__ - Memory Optimization")
    print("=" * 60)

    import sys

    obj_without = WithoutSlots(1, 2)
    obj_with = WithSlots(1, 2)

    size_without = sys.getsizeof(obj_without) + sys.getsizeof(obj_without.__dict__)
    size_with = sys.getsizeof(obj_with)

    print(f"Without __slots__: {size_without} bytes")
    print(f"With __slots__:    {size_with} bytes")
    print(f"Savings: {size_without - size_with} bytes per instance")

    # Can't add new attributes
    obj_without.z = 3  # OK
    try:
        obj_with.z = 3  # Error
    except AttributeError as e:
        print(f"\nSlots prevent new attrs: {e}")

    print("-" * 60)


# =============================================================================
# 9. Property Decorator
# =============================================================================

class Circle:
    """Demonstrate property decorator."""

    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        """Getter."""
        return self._radius

    @radius.setter
    def radius(self, value):
        """Setter with validation."""
        if value < 0:
            raise ValueError("Radius must be non-negative")
        self._radius = value

    @property
    def area(self):
        """Computed property (read-only)."""
        import math
        return math.pi * self._radius ** 2

    @radius.deleter
    def radius(self):
        """Deleter."""
        print("Deleting radius")
        del self._radius


def demo_property():
    """Demonstrate property decorator."""
    print("\n" + "=" * 60)
    print("9. PROPERTY DECORATOR")
    print("=" * 60)

    c = Circle(5)
    print(f"Radius: {c.radius}")
    print(f"Area: {c.area:.2f}")

    c.radius = 10
    print(f"New radius: {c.radius}")
    print(f"New area: {c.area:.2f}")

    try:
        c.radius = -1
    except ValueError as e:
        print(f"Validation: {e}")

    print("-" * 60)


# =============================================================================
# Summary
# =============================================================================

def print_summary():
    """Print summary of advanced concepts."""
    print("\n" + "=" * 60)
    print("ADVANCED PYTHON SUMMARY")
    print("=" * 60)
    print("""
Decorators:
  - Wrap functions/classes to add behavior
  - Use @functools.wraps to preserve metadata
  - Can take arguments (decorator factory)

Context Managers:
  - Ensure cleanup with __enter__/__exit__
  - Use @contextlib.contextmanager for simple cases
  - Handle exceptions properly

Generators:
  - Lazy evaluation, memory efficient
  - Use yield to produce values
  - Can receive values with send()

Descriptors:
  - Control attribute access
  - Implement __get__, __set__, __delete__
  - Foundation for property, classmethod, etc.

Metaclasses:
  - Control class creation
  - Use for frameworks, registries, validation
  - Usually overkill - prefer decorators

__slots__:
  - Memory optimization
  - Prevents dynamic attributes
  - Faster attribute access
    """)
    print("=" * 60)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\nAdvanced Python Concepts Tutorial")
    print("=" * 60)

    demo_decorators()
    demo_class_decorators()
    demo_context_managers()
    demo_generators()
    demo_generator_coroutine()
    demo_descriptors()
    demo_metaclasses()
    demo_slots()
    demo_property()
    print_summary()

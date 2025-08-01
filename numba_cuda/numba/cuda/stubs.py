"""
This scripts specifies all PTX special objects.
"""

import numpy as np
from collections import defaultdict
import functools
import itertools
from inspect import Signature, Parameter


class Stub(object):
    """
    A stub object to represent special objects that are meaningless
    outside the context of a CUDA kernel
    """

    _description_ = "<ptx special value>"
    __slots__ = ()  # don't allocate __dict__

    def __new__(cls):
        raise NotImplementedError("%s is not instantiable" % cls)

    def __repr__(self):
        return self._description_


def stub_function(fn):
    """
    A stub function to represent special functions that are meaningless
    outside the context of a CUDA kernel
    """

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        raise NotImplementedError("%s cannot be called from host code" % fn)

    return wrapped


# -------------------------------------------------------------------------------
# Thread and grid indices and dimensions


class Dim3(Stub):
    """A triple, (x, y, z)"""

    _description_ = "<Dim3>"

    @property
    def x(self):
        pass

    @property
    def y(self):
        pass

    @property
    def z(self):
        pass


class threadIdx(Dim3):
    """
    The thread indices in the current thread block. Each index is an integer
    spanning the range from 0 inclusive to the corresponding value of the
    attribute in :attr:`numba.cuda.blockDim` exclusive.
    """

    _description_ = "<threadIdx.{x,y,z}>"


class blockIdx(Dim3):
    """
    The block indices in the grid of thread blocks. Each index is an integer
    spanning the range from 0 inclusive to the corresponding value of the
    attribute in :attr:`numba.cuda.gridDim` exclusive.
    """

    _description_ = "<blockIdx.{x,y,z}>"


class blockDim(Dim3):
    """
    The shape of a block of threads, as declared when instantiating the kernel.
    This value is the same for all threads in a given kernel launch, even if
    they belong to different blocks (i.e. each block is "full").
    """

    _description_ = "<blockDim.{x,y,z}>"


class gridDim(Dim3):
    """
    The shape of the grid of blocks. This value is the same for all threads in
    a given kernel launch.
    """

    _description_ = "<gridDim.{x,y,z}>"


class warpsize(Stub):
    """
    The size of a warp. All architectures implemented to date have a warp size
    of 32.
    """

    _description_ = "<warpsize>"


class laneid(Stub):
    """
    This thread's lane within a warp. Ranges from 0 to
    :attr:`numba.cuda.warpsize` - 1.
    """

    _description_ = "<laneid>"


# -------------------------------------------------------------------------------
# Array creation


class shared(Stub):
    """
    Shared memory namespace
    """

    _description_ = "<shared>"

    @stub_function
    def array(shape, dtype, alignment=None):
        """
        Allocate a shared array of the given *shape*, *type*, and, optionally,
        *alignment*.  *shape* is either an integer or a tuple of integers
        representing the array's dimensions.  *type* is a :ref:`Numba type
        <numba-types>` of the elements needing to be stored in the array.
        *alignment* is an optional integer specifying the byte alignment of
        the array.  When specified, it must be a power of two, and a multiple
        of the size of a pointer (8 bytes).  When not specified, the array is
        allocated with an alignment appropriate for the supplied *dtype*.

        The returned array-like object can be read and written to like any
        normal device array (e.g. through indexing).
        """


class local(Stub):
    """
    Local memory namespace
    """

    _description_ = "<local>"

    @stub_function
    def array(shape, dtype, alignment=None):
        """
        Allocate a local array of the given *shape*, *type*, and, optionally,
        *alignment*.  *shape* is either an integer or a tuple of integers
        representing the array's dimensions.  *type* is a :ref:`Numba type
        <numba-types>` of the elements needing to be stored in the array.
        *alignment* is an optional integer specifying the byte alignment of
        the array.  When specified, it must be a power of two, and a multiple
        of the size of a pointer (8 bytes).  When not specified, the array is
        allocated with an alignment appropriate for the supplied *dtype*.

        The array is private to the current thread, and resides in global
        memory.  An array-like object is returned which can be read and
        written to like any standard array (e.g. through indexing).
        """


class const(Stub):
    """
    Constant memory namespace
    """

    @stub_function
    def array_like(ndarray):
        """
        Create a const array from *ndarry*. The resulting const array will have
        the same shape, type, and values as *ndarray*.
        """


# -------------------------------------------------------------------------------
# warp level operations


class syncwarp(Stub):
    """
    syncwarp(mask=0xFFFFFFFF)

    Synchronizes a masked subset of threads in a warp.
    """

    _description_ = "<warp_sync()>"


class vote_sync_intrinsic(Stub):
    """
    vote_sync_intrinsic(mask, mode, predictate)

    Nvvm intrinsic for performing a reduce and broadcast across a warp
    docs.nvidia.com/cuda/nvvm-ir-spec/index.html#nvvm-intrin-warp-level-vote
    """

    _description_ = "<vote_sync()>"


class match_any_sync(Stub):
    """
    match_any_sync(mask, value)

    Nvvm intrinsic for performing a compare and broadcast across a warp.
    Returns a mask of threads that have same value as the given value from
    within the masked warp.
    """

    _description_ = "<match_any_sync()>"


class match_all_sync(Stub):
    """
    match_all_sync(mask, value)

    Nvvm intrinsic for performing a compare and broadcast across a warp.
    Returns a tuple of (mask, pred), where mask is a mask of threads that have
    same value as the given value from within the masked warp, if they
    all have the same value, otherwise it is 0. Pred is a boolean of whether
    or not all threads in the mask warp have the same warp.
    """

    _description_ = "<match_all_sync()>"


class activemask(Stub):
    """
    activemask()

    Returns a 32-bit integer mask of all currently active threads in the
    calling warp. The Nth bit is set if the Nth lane in the warp is active when
    activemask() is called. Inactive threads are represented by 0 bits in the
    returned mask. Threads which have exited the kernel are always marked as
    inactive.
    """

    _description_ = "<activemask()>"


class lanemask_lt(Stub):
    """
    lanemask_lt()

    Returns a 32-bit integer mask of all lanes (including inactive ones) with
    ID less than the current lane.
    """

    _description_ = "<lanemask_lt()>"


# -------------------------------------------------------------------------------
# memory fences


class threadfence_block(Stub):
    """
    A memory fence at thread block level
    """

    _description_ = "<threadfence_block()>"


class threadfence_system(Stub):
    """
    A memory fence at system level: across devices
    """

    _description_ = "<threadfence_system()>"


class threadfence(Stub):
    """
    A memory fence at device level
    """

    _description_ = "<threadfence()>"


# -------------------------------------------------------------------------------
# bit manipulation


class popc(Stub):
    """
    popc(x)

    Returns the number of set bits in x.
    """


class brev(Stub):
    """
    brev(x)

    Returns the reverse of the bit pattern of x. For example, 0b10110110
    becomes 0b01101101.
    """


class clz(Stub):
    """
    clz(x)

    Returns the number of leading zeros in z.
    """


class ffs(Stub):
    """
    ffs(x)

    Returns the position of the first (least significant) bit set to 1 in x,
    where the least significant bit position is 1. ffs(0) returns 0.
    """


# -------------------------------------------------------------------------------
# comparison and selection instructions


class selp(Stub):
    """
    selp(a, b, c)

    Select between source operands, based on the value of the predicate source
    operand.
    """


# -------------------------------------------------------------------------------
# single / double precision arithmetic


class fma(Stub):
    """
    fma(a, b, c)

    Perform the fused multiply-add operation.
    """


class cbrt(Stub):
    """ "
    cbrt(a)

    Perform the cube root operation.
    """


# -------------------------------------------------------------------------------
# atomic


class atomic(Stub):
    """Namespace for atomic operations"""

    _description_ = "<atomic>"

    class add(Stub):
        """add(ary, idx, val)

        Perform atomic ``ary[idx] += val``. Supported on int32, float32, and
        float64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class sub(Stub):
        """sub(ary, idx, val)

        Perform atomic ``ary[idx] -= val``. Supported on int32, float32, and
        float64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class and_(Stub):
        """and_(ary, idx, val)

        Perform atomic ``ary[idx] &= val``. Supported on int32, int64, uint32
        and uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class or_(Stub):
        """or_(ary, idx, val)

        Perform atomic ``ary[idx] |= val``. Supported on int32, int64, uint32
        and uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class xor(Stub):
        """xor(ary, idx, val)

        Perform atomic ``ary[idx] ^= val``. Supported on int32, int64, uint32
        and uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class inc(Stub):
        """inc(ary, idx, val)

        Perform atomic ``ary[idx] += 1`` up to val, then reset to 0. Supported
        on uint32, and uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class dec(Stub):
        """dec(ary, idx, val)

        Performs::

           ary[idx] = val if (ary[idx] == 0) or (ary[idx] > val) else ary[idx] - 1

        Supported on uint32, and uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class exch(Stub):
        """exch(ary, idx, val)

        Perform atomic ``ary[idx] = val``. Supported on int32, int64, uint32 and
        uint64 operands only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class max(Stub):
        """max(ary, idx, val)

        Perform atomic ``ary[idx] = max(ary[idx], val)``.

        Supported on int32, int64, uint32, uint64, float32, float64 operands
        only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class min(Stub):
        """min(ary, idx, val)

        Perform atomic ``ary[idx] = min(ary[idx], val)``.

        Supported on int32, int64, uint32, uint64, float32, float64 operands
        only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class nanmax(Stub):
        """nanmax(ary, idx, val)

        Perform atomic ``ary[idx] = max(ary[idx], val)``.

        NOTE: NaN is treated as a missing value such that:
        nanmax(NaN, n) == n, nanmax(n, NaN) == n

        Supported on int32, int64, uint32, uint64, float32, float64 operands
        only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class nanmin(Stub):
        """nanmin(ary, idx, val)

        Perform atomic ``ary[idx] = min(ary[idx], val)``.

        NOTE: NaN is treated as a missing value, such that:
        nanmin(NaN, n) == n, nanmin(n, NaN) == n

        Supported on int32, int64, uint32, uint64, float32, float64 operands
        only.

        Returns the old value at the index location as if it is loaded
        atomically.
        """

    class compare_and_swap(Stub):
        """compare_and_swap(ary, old, val)

        Conditionally assign ``val`` to the first element of an 1D array ``ary``
        if the current value matches ``old``.

        Supported on int32, int64, uint32, uint64 operands only.

        Returns the old value as if it is loaded atomically.
        """

    class cas(Stub):
        """cas(ary, idx, old, val)

        Conditionally assign ``val`` to the element ``idx`` of an array
        ``ary`` if the current value of ``ary[idx]`` matches ``old``.

        Supported on int32, int64, uint32, uint64 operands only.

        Returns the old value as if it is loaded atomically.
        """


# -------------------------------------------------------------------------------
# timers


class nanosleep(Stub):
    """
    nanosleep(ns)

    Suspends the thread for a sleep duration approximately close to the delay
    `ns`, specified in nanoseconds.
    """

    _description_ = "<nansleep()>"


# -------------------------------------------------------------------------------
# vector types


def make_vector_type_stubs():
    """Make user facing objects for vector types"""
    vector_type_stubs = []
    vector_type_prefix = (
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "float32",
        "float64",
    )
    vector_type_element_counts = (1, 2, 3, 4)
    vector_type_attribute_names = ("x", "y", "z", "w")

    for prefix, nelem in itertools.product(
        vector_type_prefix, vector_type_element_counts
    ):
        type_name = f"{prefix}x{nelem}"
        attr_names = vector_type_attribute_names[:nelem]

        vector_type_stub = type(
            type_name,
            (Stub,),
            {
                **{attr: lambda self: None for attr in attr_names},
                **{
                    "_description_": f"<{type_name}>",
                    "__signature__": Signature(
                        parameters=[
                            Parameter(
                                name=attr_name, kind=Parameter.POSITIONAL_ONLY
                            )
                            for attr_name in attr_names[:nelem]
                        ]
                    ),
                    "__doc__": f"A stub for {type_name} to be used in "
                    "CUDA kernels.",
                },
                **{"aliases": []},
            },
        )
        vector_type_stubs.append(vector_type_stub)
    return vector_type_stubs


def map_vector_type_stubs_to_alias(vector_type_stubs):
    """For each of the stubs, create its aliases.

    For example: float64x3 -> double3
    """
    # C-compatible type mapping, see:
    # https://numpy.org/devdocs/reference/arrays.scalars.html#integer-types
    base_type_to_alias = {
        "char": f"int{np.dtype(np.byte).itemsize * 8}",
        "short": f"int{np.dtype(np.short).itemsize * 8}",
        "int": f"int{np.dtype(np.intc).itemsize * 8}",
        "long": f"int{np.dtype(np.int_).itemsize * 8}",
        "longlong": f"int{np.dtype(np.longlong).itemsize * 8}",
        "uchar": f"uint{np.dtype(np.ubyte).itemsize * 8}",
        "ushort": f"uint{np.dtype(np.ushort).itemsize * 8}",
        "uint": f"uint{np.dtype(np.uintc).itemsize * 8}",
        "ulong": f"uint{np.dtype(np.uint).itemsize * 8}",
        "ulonglong": f"uint{np.dtype(np.ulonglong).itemsize * 8}",
        "float": f"float{np.dtype(np.single).itemsize * 8}",
        "double": f"float{np.dtype(np.double).itemsize * 8}",
    }

    base_type_to_vector_type = defaultdict(list)
    for stub in vector_type_stubs:
        base_type_to_vector_type[stub.__name__[:-2]].append(stub)

    for alias, base_type in base_type_to_alias.items():
        vector_type_stubs = base_type_to_vector_type[base_type]
        for stub in vector_type_stubs:
            nelem = stub.__name__[-1]
            stub.aliases.append(f"{alias}{nelem}")


_vector_type_stubs = make_vector_type_stubs()
map_vector_type_stubs_to_alias(_vector_type_stubs)

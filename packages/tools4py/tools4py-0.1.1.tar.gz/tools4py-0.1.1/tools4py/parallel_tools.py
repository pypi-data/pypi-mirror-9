from mpi4py import MPI
_comm = MPI.COMM_WORLD
_rank = _comm.rank
_size = _comm.size

def ideally_parallel(iterable):
    """Iterate over an iterable in parallel with mpi4py.

    Example:
        script.py:
            from tools4py import ideally_parallel
            for i in ideally_parallel(range(10)):
                print i
        mpirun -np 4 python script.py
    """
    for i, it in enumerate(iterable):
        if i % _size == _rank:
            yield it

def parallel_map(function, objects):
    results = []
    for o in ideally_parallel(objects):
        results.append(function(o))
    results = _comm.allgather(results)
    # Return order to the world
    return [results[i % _size][i // _size] for i in range(len(objects))]

def parallel_map_reduce(function, objects, reduce_function):
    results = []
    for o in ideally_parallel(objects):
        results.append(function(o))
    if len(results) > 0:
        results = reduce_function(results)
    else:
        results = None
    results = _comm.allgather(results)
    return reduce_function(results)

def comm_rank_size():
    return _comm, _rank, _size

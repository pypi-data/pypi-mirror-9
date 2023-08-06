from mpi4py import MPI
_comm = MPI.COMM_WORLD
_rank = _comm.rank
_size = _comm.size

def ideally_parallel(iterable):
    for i, it in enumerate(iterable):
        if i % _size == _rank:
            yield it

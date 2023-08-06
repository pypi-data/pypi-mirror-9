'''
This routine looks after the MPI-parallelization bits.
It takes care of the case that mpi4py is not available,
or that is it apparently available, but not useable.
'''

parallel = parallelbuiltin

if parallel:
    try:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    except:
        comm = None
        rank = 0
        size = 1
else:
    comm = None
    rank = 0
    size = 1

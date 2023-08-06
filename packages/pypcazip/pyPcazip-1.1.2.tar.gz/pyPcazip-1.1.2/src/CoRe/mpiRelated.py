'''
This routine looks after the MPI-parallelization bits.
It takes care of the case that mpi4py is not available,
or that is it apparently available, but not useable.
'''

try:
    from mpi4py import MPI
    parallel = True
except:
    print ''
    print 'MPI does not seem to be available, maybe a batch script is needed for it to work.'
    print 'No worries, the serial version of the code is going to be used now.'
    print ''
    parallel = False

if parallel:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
else:
    comm = None
    rank = 0
    size = 1

#!/usr/bin/python
'''
Implements the Fasu (Filtered And Sliced Universe) class, and
the Cofasu (Collection of Fasus) class.
'''
import MDAnalysis as mda
import MDPlus
import numpy as np
from MDAnalysis.analysis.align import *
from MDAnalysis.coordinates.base import Timestep
from time import time
import sys
import logging as log
import tempfile
from os import remove


# EPCC, MPI Parallelization
import mpiRelated

comm = mpiRelated.comm
parallel = mpiRelated.parallel
rank = mpiRelated.rank
size = mpiRelated.size
if parallel:
    from mpi4py import MPI

'''
Two little utility functions. Both work on (N,3) numpy arrays of
coordinates and do least-squares fitting and rmsd calculations
respectively. The USP is that they will not fall over if there are
<3 atoms in a coordinate set.
'''
def aatb(mobile,target,weights=None):
    '''
    Least squares fits the coordinates in mobile to the coordinates in
    target, with optional mass weighting. Both coordinate sets should be
    (N,3) numpy arrays. If weights is given, it should be an array of
    length N. The USP of this method is that it works for N >= 1 whereas
    most standard methods require N >= 3.

    >>> a = np.array([[1,2,3],[3,4,2],[3,4,5],[4,5,7]])
    >>> b = np.array([[2,1,3],[4,2,3],[3,5,5],[4,2,2]])
    >>> fit = np.array(
    ... [[ 1.12516775,  0.79573647,  3.76775837],
    ...  [ 4.09962641,  0.55448804,  4.07499587],
    ...  [ 3.4250583,   3.25851991,  2.9645142 ],
    ...  [ 4.35014754,  5.39125558,  2.19273156]])
    >>> print np.allclose(aatb(a,b),fit)
    True

    >>> w = np.array([1,12,16,1])
    >>> wfit = np.array(
    ... [[ 1.8421418,   0.33714323,  2.23635022],
    ... [ 4.75590912,  1.04010775,  2.36205162],
    ... [ 3.14411401,  3.22518467,  3.6378084 ],
    ... [ 3.25783507,  5.39756436,  4.76378975]])
    >>> print np.allclose(aatb(a,b,weights=w),wfit)
    True

    >>> print aatb(a,a)
    [[ 1.  2.  3.]
     [ 3.  4.  2.]
     [ 3.  4.  5.]
     [ 4.  5.  7.]]

    >>> print aatb(a[0],b[0])
    [2 1 3]

    >>> fit2 = np.array(
    ... [[ 1.65835921,  0.82917961,  3.        ],
    ...  [ 4.34164079,  2.17082039,  3.        ]])
    >>> print np.allclose(aatb(a[0:2],b[0:2]),fit2)
    True

    >>> print aatb(a,b[0:3])
    Traceback (most recent call last):
        ...
    ValueError: coordinate sets not same size

    '''
    if mobile.shape != target.shape:
        raise ValueError("coordinate sets not same size")
    if len(np.atleast_2d(mobile))==1:
# a single point - just place at target:
       fitted = target
    elif len(np.atleast_2d(mobile))==2:
# a vector - align mobile with target:
       midpoint = target.mean(axis=0)
       targetvector = target[1]-target[0]
       mobilevector = mobile[1]-mobile[0]
       tvlength = np.sqrt(np.dot(targetvector,targetvector))
       mvlength = np.sqrt(np.dot(mobilevector,mobilevector))
       scalefactor = mvlength/tvlength
       newvector = targetvector*scalefactor/2
       fitted = np.array([midpoint-newvector,midpoint+newvector])
    else:
# at least three points - use standard methods:
        lmob = mobile-mobile.mean(axis=0)
        targ_com = target.mean(axis=0)
        ltarg = target-targ_com
        R,rms = rotation_matrix(ltarg,lmob,weights=weights)
        fitted = np.dot(lmob, np.array(R))
        fitted = fitted+targ_com
    return fitted

def rmsd(c1,c2,R=False):
    '''
    RMSD between the coordinates in c1 and those in c2.  Both coordinate
    sets should be (N,3) numpy arrays.  The USP of this method is that it
    works for N >= 1 whereas most standard methods require N >= 3. If the
    R argument is set the rotation matrix is also returned.

    >>> a = np.array([[1,2,3],[3,4,2],[3,4,5],[4,5,7]])
    >>> b = np.array([[2,1,3],[4,2,3],[3,5,5],[4,2,2]])
    >>> print np.allclose(rmsd(a,b),2.43251656802)
    True

    >>> print rmsd(a[0],b[0])
    0.0

    >>> print rmsd(a,b[:3])
    Traceback (most recent call last):
        ...
    ValueError: coordinate sets not same size
    '''

    if c1.shape != c2.shape:
        raise ValueError("coordinate sets not same size")

    local1 = c1-c1.mean(axis=0)
    local2 = c2-c2.mean(axis=0)
    if len(np.atleast_2d(c1))==1:
       rms = 0.0
       R=False
    elif len(np.atleast_2d(c1))==2:
        R=False
        fitted1 = aatb(local1,local2)
        diff = fitted1-local2
        rms = np.sqrt((diff*diff).mean())
    else:
        Rot,rms = rotation_matrix(local1,local2)
    if R:
        return rms, Rot
    else:
        return rms

class Fasu:
    def __init__(self, topology, trajectory, filter='name *', slice=None,
                start=0, stop=None, step=1, format=None, owner=0, 
                tfunc=None, **kwargs):
        '''
        Initialises a new fasu object, The optional arguments provide an
        (MDAnalysis-style) selection string, and the others the first and
        last frames in the trajectory to be used, and the stepsize to iterate
        between them. If stop=None then the value will be taken from the
        trajectory file. If it is provided, it will be checked for sanity
        against the number of snapshots in the trajectory file. If a value
        for slice is given in the form "start:stop:step", it will override
        any individual start, stop, or step argument. The 'format' keyword is
        passed directly to MDAnalysis as a hint as to the trajectory format.
        BE AWARE: Cofasu uses zero-based indexing!
        The 'owner' argument is for use with MPI. It identifies which
        process 'owns' the Fasu, and so has actual access to the associated
        trajectory file. Fasus created by processes that don't 'own' them
        are not fully initialised until their sync() method is called; this
        may be done any time after their creation, but is also done implicitly
        when they are added to a cofasu so is not something most users will
        need to deal with.
        Tfunc allows a user-supplied function to be added, that will
        manipulate coordinates before they are returned to the user through
        the coords() methods. The function must conform to the signature:
        atomSelection = tfunc(atomSelection, **kwargs). One key use is in
        supplying functions that fix PBC issues on the fly.
        kwargs are passed straight to the MDAnalysis Universe. The main use is
        for reading numpy arrays as trajectories, but they also suppy extra
        arguments needed for the optional tfunc.
        '''
        self.topology = topology
        self.trajectory = trajectory
        self.format = format
        self.selection = filter
        self.slice = slice
        self.owner = owner
        self.tfunc = tfunc
        self.kwargs = kwargs

        if rank == owner:
#            print 'process ',owner, 'reading ',self.trajectory
            self.u = mda.Universe(self.topology,self.trajectory,format=self.format,**kwargs)
            self.totframes = self.u.trajectory.numframes
            self.sel = self.u.selectAtoms(self.selection)
            self.masses = self.sel.masses()
            self.names = self.sel.names()
            self.natoms = len(self.sel)
            self.start = start
            if stop == None:
                self.stop = self.totframes-1
            else:
                self.stop = stop
            self.step = step
            if self.slice is not None:
                self.setslice(slice)
            else:
                self.setstart(start)
                self.setstop(stop)
                self.setstep(step)

        else:
        # initialise with some dummy data
            self.u = None
            self.sel = None
            self.start = start
            self.stop = stop
            self.slice = slice
            self.step = step
            self.totframes = 0
            self.natoms = 0
            self.masses = np.zeros(self.natoms)
            self.names = ['X' for i in range(self.natoms)]

    def sync(self):
        '''
        call this routine after a fasu has been initialised
        to ensure all processes have the correct data
        '''
        if parallel:
            self.start = comm.bcast(self.start,root=self.owner)
            self.stop = comm.bcast(self.stop,root=self.owner)
            self.step = comm.bcast(self.step,root=self.owner)
            self.slice = comm.bcast(self.slice,root=self.owner)
            self.totframes = comm.bcast(self.totframes,root=self.owner)
            self.natoms = comm.bcast(self.natoms,root=self.owner)
            self.massess = comm.bcast(self.masses,root=self.owner)
            self.names = comm.bcast(self.names,root=self.owner)

    def setstart(self,start):
        '''
        Set the first snapshot to be considered, with sanity checking.
        '''
        if start >= self.totframes:
            raise ValueError('value for start ({}) exceeds number of frames in the trajectory ({}).'.format(start, self.totframes))
        if (self.stop != None) and (start > self.stop):
            raise ValueError('value for start ({}) exceeds value for stop ({}).'.format(start,self.stop))
        self.start = start
        if self.start < 0:
            self.start = 0

    def setstop(self,stop):
        '''
        Set the last snapshot, with sanity checking.
        '''
        tmpstop = self.stop

        if stop==None:
            self.stop = self.totframes - 1
        else:
            self.stop = stop

        if self.stop < 0:
            self.stop = self.totframes + self.stop
        if self.stop < self.start:
            self.stop = tmpstop
            raise ValueError('value for stop is less than  value for start.')
        if self.stop >= self.totframes:
            self.stop = self.totframes - 1

    def setstep(self,step):
        '''
        Set the stepsize, with sanity checking.
        '''
        if step < 1:
            raise ValueError('stepsize must be positive.')
        self.step = step

    def setslice(self,slice):
        '''
        Set the start, stop, and step paremeters based on the slice
        string, which takes the form "start:stop:step". Missing values
        are dealt with in the standard pythonic way.
        '''
        sl = slice
        nc = slice.count(':')
        if nc == 0:
            sl = sl+'::'
        elif nc == 1:
            sl = sl+':'

        start = sl.partition(':')[0].partition(':')[0]
        stop = sl.partition(':')[2].partition(':')[0]
        step = sl.partition(':')[2].partition(':')[2]

        if start.isdigit():
            self.setstart(int(start))
        else:
            self.setstart(0)

        if stop.isdigit():
            self.setstop(int(stop))
        else:
            self.setstop(-1)

        if step.isdigit():
            self.setstep(int(step))
        else:
            self.setstep(1)

    def setfilter(self,filter):

        self.selection = filter
        if rank == self.owner:
            self.sel = self.u.selectAtoms(self.selection)
            self.natoms = len(self.sel)
        else:
            self.sel = None
        if parallel:
            self.natoms = comm.bcast(self.natoms,root=self.owner)

    def numframes(self):
        '''
        Returns the actual number of frames that will be considered.
        '''
        n = 1+(self.stop-self.start)/self.step
        return n

    def coords(self,snap):
        '''
        Returns a (natoms,3) numpy array of the selected coordinates
        at the chosen snapshot (zero-based).
        '''
        if rank == self.owner:
            nf = self.numframes()
            if snap < 0:
                snap = nf+snap
            if snap >= nf or snap < 0:
                raise ValueError('snapshot out of range.'+str(snap))

            snp = self.start + snap * self.step
            if snp < (self.u.trajectory.frame-1):
               self.u.trajectory.rewind()
            while (self.u.trajectory.frame-1) < snp:
               try:
                   self.u.trajectory.next()
               except EOFError:
                   print "EOFError trying to access snapshot ",snap
                   raise EOFError
            if self.tfunc is not None:
                crds = self.tfunc(self.sel,**self.kwargs).ts._pos
            else:
                crds =  self.sel.ts._pos
        else:
            print 'Error - process ',rank,' trying to access fasu owned by ',self.owner
            exit(1)

        return crds


    def fitted_sum(self, target, weights=None):
        '''
        Returns the sum of all the snapshots in the Fasu, as a (N,3)
        numpy array, after they have all been least-squares fitted
        to target. If weights is a list of masses, then weighted
        fitting will be done.
        '''

        if rank == self.owner:
#            print 'process ',rank, 'fitted_sum on: ',self.trajectory
            self.target = target
            sum = np.zeros((self.natoms,3))
            for i in range(self.numframes()):
                mob = self.coords(i)
                sum += aatb(mob,self.target,weights=weights)
        else:
            print 'Error - process ',rank,' trying to access fasu owned by ',self.owner
            exit(1)

        return sum

    def cov(self, target, weights=None, preload=True):
        '''
        Returns the covariance matrix for the trajectory,
        after least-squares fitting to target.
        '''

        if rank == self.owner:

            if preload:
                if rank == 0:
                    log.info("Calculating covariance matrix fast method")
                try:
                    trj = np.zeros((self.numframes(), self.natoms*3))
                except MemoryError:
                    print "The input file is too big to be preloaded. Please, try to call pyPcazip with the --nopreload option"
                    sys.exit(0)
                for i in range(self.numframes()):
                    mob = aatb(self.coords(i), target, weights=weights)-target
                    trj[i,:] = mob.flatten()
                covar = np.dot(trj.T, trj.conj())/self.numframes()
            else:

                log.info("Calculating covariance matrix big files method")
                max_ts = 10000 # TODO this should be an argument, and dependant on num atoms
                num_blocks = self.numframes()/max_ts
                ts_out = self.numframes() - (max_ts * num_blocks) # Equivalent to ts_out = self.numframes() % max_ts

                if ts_out != 0:
                    # First block it will process the ts_out snaps witch is the same as the module (self.numframes() % max_ts)
                    covar = np.zeros((self.natoms*3, self.natoms*3))
                    trj = np.zeros((ts_out, self.natoms*3))
                    for j in range(ts_out):
                        mob = aatb(self.coords(j), target, weights=weights)-target
                        mob = mob.flatten()
                        trj[j,:] = mob
                    covar = np.dot(trj.T, trj.conj())/ts_out

                total_ts = ts_out  #Current number of processed frames

                # Loop the rest of blocks, each one of max_ts size in order to contain the amount of used memory
                for i in range(num_blocks):
                    trj = np.zeros((max_ts, self.natoms*3))
                if rank == 0:
                    log.info("Calculating covariance matrix big files method")
                """
                num_vars = self.natoms*3
                aver = np.zeros(num_vars)
                for i in range(self.numframes()):
                    mob = aatb(self.coords(i), target, weights=weights)-target
                    mob = mob.flatten()
                    aver += mob

                # Code to monitor the estimated time of calculus ********************************
                loops = (num_vars*(num_vars+1)/2)*self.numframes()
                """


                max_ts = 1000 # TODO this should be an argument, and dependant on num atoms
                num_blocks = self.numframes()/max_ts
                ts_extra = self.numframes()%max_ts
                covar = np.zeros((self.natoms*3, self.natoms*3))

                # LOOP OVER FULL BLOCKS
                trj = np.zeros((max_ts, self.natoms*3))
                for i in range(num_blocks):
                    for j in range(max_ts):
                        index = total_ts + j
                        mob = aatb(self.coords(index), target, weights=weights)-target
                        mob = mob.flatten()
                        trj[j,:] = mob
                    covar += np.dot(trj.T, trj.conj())

                    # Add the current block_covar to the total covar matrix
                    covar = (covar*total_ts + block_covar*max_ts)/(total_ts+max_ts)
                    total_ts += max_ts

                # REMAINDER BLOCK
                trj = np.zeros((ts_extra, self.natoms*3))
                for j in range(ts_extra):
                    index = num_blocks*max_ts + j
                    mob = aatb(self.coords(index), target, weights=weights)-target
                    mob = mob.flatten()
                    trj[j,:] = mob
                covar += np.dot(trj.T, trj.conj())
                covar = covar/self.numframes()

        else:
            print 'Error - process ', rank, ' trying to access fasu owned by ', self.owner
            exit(1)

        #np.savetxt(self.trajectory+str(preload)+".txt",covar)
        return covar

class Cofasu:
    def __init__(self, fasu, check=None):
        '''
        Initialises a new cofasu object. The argument may be a single fasu
        or a list of them. The optional 'check' argument is used if more than
        one fasu is to be added to the Cofasu. If check="masses", then in
        addition to the obligatory check that all fasus have the same
        number of atoms, a check will be made that they match, in sequence,
        by atomic mass too. If check="names" then the atom names will be
        checked instead.
        '''
        self.fasulist = []
        if isinstance(fasu,list):
            self.fasulist.append(fasu[0])
            fasu[0].sync()
            self.natoms = fasu[0].natoms
            for i in range(1,len(fasu)):
                self.add(fasu[i], check=None)
        else:
            self.fasulist.append(fasu)
            fasu.sync()
            self.natoms = fasu.natoms

    def __len__(self):
        return len(self.fasulist)

    def __getitem__(self,key):
        return Cofasu(self.fasulist[key])

    def add(self, fasu, check=None):
        '''
        Add a new fasu to the cofasu, if it is congruent (has right number of
        atoms), and, if the check is asked for, that the atomic masses match,
        or the atom names match.
        '''
        fasu.sync()
        if fasu.natoms != self.natoms:
            raise ValueError('fasu has wrong number of atoms.')
        if check == 'names':
            m1 = self.fasulist[0].names()
            m2 = fasu.names()
            if (m1 == m2):
                self.fasulist.append(fasu)
            else:
                raise ValueError("fasu atom names don't match.")
        if check == 'masses':
            m1 = self.fasulist[0].masses()
            m2 = fasu.masses()
            if (m1 == m2).all():
                self.fasulist.append(fasu)
            else:
                raise ValueError("fasu atom masses don't match.")
        else:
            self.fasulist.append(fasu)

    def numframes(self):
        '''
        Returns the total number of frames in the cofasu
        '''
        totframes = 0
        nframes = 0
        for fasu in self.fasulist:
             nframes += fasu.numframes()
        return nframes
#            if rank == fasu.owner:
#                nframes += fasu.numframes()
#        if parallel:
#            totframes = comm.allreduce(nframes, MPI.SUM)
#        else:
#            totframes = nframes
#        return totframes

    def coords(self,snap,target=None,weights=None):
        '''
        Returns a (natom,3) numpy array of the coordinates of the
        selected snapshot (zero-based). If target is given, then
        the coordinates returned are first least-squares fitted
        to this structure, with optional mass-weighting.
        '''
        # first some sanity-checking:
        if snap < 0:
            snap = snap + self.numframes()
        if snap < 0:
            raise ValueError('snapshot out of range.')
        if snap > (self.numframes()-1):
            raise ValueError('snapshot out of range.')
        # now find which Fasu contains the desired snapshot:
        ifas = 0
        nsum = self.fasulist[ifas].numframes()
        while (nsum <= snap) and (ifas < (len(self.fasulist)-1)):
            ifas += 1
            nsum = nsum + self.fasulist[ifas].numframes()
        # now get the desired coordinates:
        nsum = nsum - self.fasulist[ifas].numframes()
        if rank == self.fasulist[ifas].owner:
            crds = self.fasulist[ifas].coords(snap-nsum)
            if target is not None:
                crds = aatb(crds,target,weights=weights)
        else:
            crds = None
        if parallel:
            crds = comm.bcast(crds, root=self.fasulist[ifas].owner)
        return crds

    def fitted_average(self, target=None, error=0.0001, weights=None, maxcyc=10):
        '''
        Calculates the global average structure after converged
        cycles of least-squares fitting. The optional argument
        "target" can specify a coordinate set ((natom,3) numpy array)
        to be used to start the process. Otherwise the first structure
        in the cofasu is used. If weights is a list of masses, then
        weighted fitting will be done.
        '''
        if target is None:
            self.target = self.coords(0)
        else:
            self.target = target

        err = error + 1.0
        icyc = 0
        while err > error and icyc < maxcyc:
            avg = np.zeros((self.natoms,3))
            totavg = np.zeros((self.natoms,3))
            for f in self.fasulist:
                if rank == f.owner:
                    avg += f.fitted_sum(self.target, weights=weights)

            if parallel:
                totavg = comm.reduce(avg, MPI.SUM, root=0)
                totavg = comm.bcast(totavg, root=0)
            else:
                totavg = avg

            avg = totavg/self.numframes()
            err = rmsd(self.target,avg)
            self.target = avg
            icyc += 1
        return avg

    def cov(self, target=None, weights=None, preload=True):
        '''
        Calculate the covariance matrix for the Cofasu, after least-squares
        fitting of each snapshot to target (if given), with optional weights.
        '''
        try:
            covar = np.zeros((self.natoms*3,self.natoms*3))
            totcovar = np.zeros((self.natoms*3,self.natoms*3))
        except MemoryError:
            print "The system contains too many atoms ("+str(self.natoms)+"). Please, try to launch pyPcazip with an atom selection."
            sys.exit(0)

        if target is None:
            time_avg_0 = time()
            target = self.fitted_average()
            time_avg_1 = time()
            if (parallel and (rank == 0)):
                log.info('Cofasu: Time for calculating average structure: {:.2f} s\n'.format(time_avg_1-time_avg_0))
            else:
                log.info('Cofasu: Time to calculate average structure: {:.2f} s\n'.format(time_avg_1-time_avg_0))


        time_cov_0 = time()
        for f in self.fasulist:
            if rank == f.owner:
                covar += f.cov(target, weights=weights, preload=preload)*f.numframes()
        if parallel:
            totcovar = comm.reduce(covar, MPI.SUM, root=0)
            totcovar = comm.bcast(totcovar, root=0)
        else:
            totcovar = covar
        covar = totcovar/self.numframes()
        time_cov_1 = time()
        if rank == 0:
            log.info('Cofasu: Time for calculating the covariance matrix: {:.2f} s\n'.format(time_cov_1-time_cov_0))

        return covar

    def write(self, filename, start=0, end=None):
        '''
        Writes the cofasu out to the specified trajectory file. The
        neccessary topology data is taken from the first fasu - note
        that since not every fasu in a cofasu has to have the same 
        topology, this needs some caution from the user. The optional
        start and end arguments specify the range of frames to write
        (from start to end-1 inclusive).
        '''
        if end is None:
            end = self.numframes()
        else:
            end = min(self.numframes(),end)
        if rank == self.fasulist[0].owner:
            w = mda.Writer(filename, self.natoms)
        ts = Timestep(self.natoms)
        for ts_index in xrange(start,end):
            ts._pos=self.coords(ts_index)
            if rank == self.fasulist[0].owner:
                w.write(ts)
        if rank == self.fasulist[0].owner:
            w.close()

    def optcopy(self):
        '''
        Returns an optimised copy of a cofasu. A set of new, dcd format,
        trajectory files are generated, one per MPI process (size). The
        coordinates are then split equally amongst them. A corresponding
        topology file (in pdb format) is also generated. These files are
        then used to generate a new cofasu. Whether or not this is worth
        doing will depend on many factors: the format of the original
        trajectory files, how equalk in size they are, how the number of
        files compares to the number of available MPI processes, etc.
        '''
        if rank == 0:
            topfile = tempfile.NamedTemporaryFile(delete=False, suffix='.pdb').name
        else:
            topfile="dummy.pdb"
        trjlist = []
        for i in range(size):
            if rank == 0:
                trjlist.append(tempfile.NamedTemporaryFile(delete=False, suffix='.dcd').name)
            else:
                trjlist.append("dummy.dcd")
        if parallel:
            topfile = comm.bcast(topfile,root=0)
            trjlist = comm.bcast(trjlist,root=0)
        self.writepdb(topfile,self.coords(0))
        blocksize = self.numframes()/size
        if self.numframes()%size != 0:
            blocksize += 1
        start = 0
        end = blocksize
        for t in trjlist:
            self.write(t,start=start, end=end)
            start += blocksize
            end += blocksize
            end = min(end,self.numframes())

        if rank == 0:
            log.info("Files for optimised copy of cofasu created")

        f = []
        for i in range(size):
            f.append(Fasu(topfile,trjlist[i],owner=i))
        optc = Cofasu(f)
        if rank == 0:
            log.info("Optimised copy of cofasu created")
        return optc


    def writepdb(self, filename, crds):
        '''
        A naughty little hack to enable an arbitrary array of
        coordinates - that match the cofasu for shape - to be
        written out as a pdb format file, by hijacking one of
        the atomSelections in the cofasu.
        '''
        if rank == self.fasulist[0].owner:
            self.fasulist[0].sel.set_positions(crds)
            self.fasulist[0].sel.write(filename)

    def rmsd(self, frame1, frame2):
        '''
        Calculates the rmsd between two frames in a cofasu.
        '''
        f1 = self.coords(frame1)
        f2 = self.coords(frame2)

        f1 = f1 - f1.mean(axis=0)
        f2 = f2 - f2.mean(axis=0)

        return rmsd(f1,f2)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

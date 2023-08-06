"""job_stream's python module implementation.  Example usage:

class AddOne(job_stream.Job):
    def handleWork(self, work):
        self.emit(work + 1)

job_stream.work.append(8)
job_stream.work.append(9)
job_stream.run({
    'jobs': [
        { 'type': AddOne }
    ]
})
# 9 and 10 will have been printed.
"""

import _job_stream as _j

import cPickle as pickle
import multiprocessing
import traceback

# Classes waiting for _patchForMultiprocessing.  We wait until _pool is initiated
# so that A) classes inheriting from one another are rewritten backwards so that they
# execute the original method, not the override, and B) so that their methods may be
# updated between class definition and job_stream.run()
_classesToPatch = []
_pool = [ None ]
def _initMultiprocessingPool():
    """The multiprocessing pool is initialized lazily by default, to avoid
    overhead if no jobs are using multiprocessing"""
    if _pool[0] is None:
        class NoDoubleInit(object):
            def __getattribute__(self, name):
                raise ValueError("Cannot use _pool in a worker process")
        _pool[0] = NoDoubleInit()
        _pool[0] = multiprocessing.Pool()


def _decode(s):
    """Decodes an object with cPickle"""
    return pickle.loads(s)


def _encode(o):
    """Encodes an object with cPickle"""
    return pickle.dumps(o)


class Object(object):
    """A generic object with no attributes of its own."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


    def __repr__(self):
        r = [ 'job_stream.Object(' ]
        for k, v in self.__dict__.iteritems():
            r.append('{}={}, '.format(k, repr(v)))
        r.append(')')
        return ''.join(r)


class _StackAlreadyPrintedError(Exception):
    """An exception to be used if the stack trace has already been printed,
    and an exception needs to be raised just to communicate to job_stream to
    abort."""


# Initialize the encode and decode values first so that they can be used in
# debug code (if left uninitialized, any attempt to pickle something from within
# C++ code will crash with NoneType cannot be called)
_j.registerEncoding(Object, _StackAlreadyPrintedError, _encode, _decode)


class _Work(list):
    """List of initial work sent into job_stream.
    If left empty, work comes from stdin."""
work = _Work()

_localJobs = {}
_localJobId = [ 0 ]
def _localJobInit(obj):
    _localJobs[obj.id] = obj
    if hasattr(obj, 'emit'):
        obj.emit = lambda *args: obj.emitters.append(args)
    if hasattr(obj, 'recur'):
        obj.recur = lambda *args: obj.recurs.append(args)
    obj._forceCheckpoint = lambda *args: obj.forceCheckpoints.append(args)
    def obj_reset():
        obj.emitters = []
        obj.recurs = []
        obj.forceCheckpoints = []
    obj._resetLocalJob = obj_reset

    # Now call postSetup.  Note that since we haven't called reset() yet, none of the
    # arrays exist and so emit(), recur(), and _forceCheckpoint() will all crash
    try:
        obj.mPostSetup()
    except:
        traceback.print_exc()
        raise _StackAlreadyPrintedError()
def _localCallNoStore(obj, method, *args):
    if obj not in _localJobs:
        return (0, [], [], [])
    o = _localJobs[obj]
    o._resetLocalJob()
    try:
        getattr(o, method)(*args)
    except:
        traceback.print_exc()
        raise _StackAlreadyPrintedError()
    return (1, o.emitters, o.recurs, o.forceCheckpoints)
def _localCallStoreFirst(obj, method, first, *args):
    if obj not in _localJobs:
        return (0, None, [], [], [])
    o = _localJobs[obj]
    o._resetLocalJob()
    try:
        getattr(o, method)(first, *args)
    except:
        traceback.print_exc()
        raise _StackAlreadyPrintedError()
    return (1, first, o.emitters, o.recurs, o.forceCheckpoints)


def _callNoStore(obj, method, *args):
    while True:
        r = _pool[0].apply(_localCallNoStore, args = (obj.id, method) + args)
        if r[0] == 0:
            _pool[0].apply(_localJobInit, args = (obj,))
        else:
            break
    for eArgs in r[1]:
        obj.emit(*eArgs)
    for rArgs in r[2]:
        obj.recur(*rArgs)
    for fArgs in r[3]:
        obj._forceCheckpoint(*fArgs)


def _callStoreFirst(obj, method, first, *args):
    while True:
        r = _pool[0].apply(_localCallStoreFirst,
                args = (obj.id, method, first) + args)
        if r[0] == 0:
            _pool[0].apply(_localJobInit, args = (obj,))
        else:
            break
    first.__dict__ = r[1].__dict__
    for eArgs in r[2]:
        obj.emit(*eArgs)
    for rArgs in r[3]:
        obj.recur(*rArgs)
    for fArgs in r[4]:
        obj._forceCheckpoint(*fArgs)
def _hierarchicalName(cls, name = None):
    fullname = cls.__module__
    n = name or cls.__name__
    if fullname == '__main__':
        fullname = n
    else:
        fullname += '.' + n
    return fullname


class Job(_j.Job):
    """Base class for a standard job (starts with some work, and emits zero or
    more times).  Handles registration of job class with the job_stream
    system.

    Example:
    import job_stream
    class MyJob(job_stream.Job):
        '''Adds 8 to an integer or floating point number'''
        def handleWork(self, work):
            self.emit(work + 8)
    job_stream.work = [ 1, 2, 3.0 ]
    # This will print 9, 10, and 11.0
    job_stream.run({ 'jobs': [ MyJob ] })
    """
    class __metaclass__(type(_j.Job)):
        def __init__(cls, name, bases, attrs):
            type(_j.Job).__init__(cls, name, bases, attrs)

            # Derived hierarchical name, use that in config
            fullname = _hierarchicalName(cls, name)

            # Metaclasses are called for their first rendition as well, so...
            if fullname == 'job_stream.Job':
                return

            _classesToPatch.append(cls)
            _j.registerJob(fullname, cls)


    USE_MULTIPROCESSING = True
    USE_MULTIPROCESSING_doc = """If True [default {}], job_stream automatically handles
        overloading the class' methods and serializing everything so that the GIL is
        circumvented.  While this defaults to True as it is low overhead, lots of jobs
        do not need multiprocessing if they are using other python libraries or operations
        that release the GIL.""".format(USE_MULTIPROCESSING)


    @classmethod
    def _patchForMultiprocessing(cls):
        if hasattr(cls, '_MULTIPROCESSING_PATCHED'):
            return

        cls._MULTIPROCESSING_PATCHED = True
        def newInit(self):
            super(cls, self).__init__()
            _initMultiprocessingPool()
            self.id = _localJobId[0]
            _localJobId[0] += 1
        cls.__init__ = newInit

        cls.mHandleWork = cls.handleWork
        cls.handleWork = lambda self, *args: _callNoStore(self, "mHandleWork",
                *args)

        # We do not call postSetup when job_stream requests it.  This is because
        # our jobs must be set up in each thread, so we defer until it is called
        # in a thread.
        cls.mPostSetup = cls.postSetup
        cls.postSetup = lambda self: True


    def postSetup(self):
        """Called when self.config is set and the Job is fully ready for work,
        but before any work is accepted."""
        pass


    def handleWork(self, work):
        """Handle incoming work, maybe call self.emit() to generate more work
        for jobs further down the pipe."""
        raise NotImplementedError()



class Reducer(_j.Reducer):
    """Base class for a Reducer.  A Reducer combines work emitted from the last
    stage of a reduction, eventually emitting its own result to the next link
    in the processing chain.  A reduction starts when a piece of work enters
    a module guarded by a Reducer.

    Example:
    import job_stream
    class AddLetterA(job_stream.Job):
        def handleWork(self, w):
            self.emit(w + 'A')
    class CountLetters(job_stream.Reducer):
        '''Counts the number of letters passed to it'''
        def handleInit(self, store):
            store.count = 0
        def handleAdd(self, store, work):
            store.count += len(work)
        def handleJoin(self, store, other):
            store.count += other.count
        def handleDone(self, store):
            self.emit(store.count)
    job_stream.work = [ 'Hello', 'World' ]
    # Here the reduction starts at the global scope, so it will print out 12,
    # which is the original 10 letters plus the two new letter A's.
    print("First:")
    job_stream.run({
            'reducer': CountLetters,
            'jobs': [ AddLetterA ]
    })
    # This config has the reduction starting as part of the first job rather
    # than the global scope, so this will print 6 twice (once for each work that
    # we initially passed in).
    print("Second:")
    job_stream.run({
            'jobs': [
                {
                    'reducer': CountLetters,
                    'jobs': [ AddLetterA ]
                }
            ]
    })
    """
    class __metaclass__(type(_j.Reducer)):
        def __init__(cls, name, bases, attrs):
            type(_j.Reducer).__init__(cls, name, bases, attrs)

            # Derived hierarchical name, use that in config
            fullname = _hierarchicalName(cls, name)

            # Metaclasses are called for their first rendition as well, so...
            if fullname == 'job_stream.Reducer':
                return

            _j.registerReducer(fullname, cls)


    USE_MULTIPROCESSING = Job.USE_MULTIPROCESSING
    USE_MULTIPROCESSING_doc = Job.USE_MULTIPROCESSING_doc


    @classmethod
    def _patchForMultiprocessing(cls):
        if hasattr(cls, '_MULTIPROCESSING_PATCHED'):
            return

        cls._MULTIPROCESSING_PATCHED = True
        def newInit(self):
            super(cls, self).__init__()
            _initMultiprocessingPool()
            self.id = _localJobId[0]
            _localJobId[0] += 1
        cls.__init__ = newInit

        for oldName in [ 'handleInit', 'handleAdd', 'handleJoin', 'handleDone' ]:
            newName = 'm' + oldName[0].upper() + oldName[1:]
            setattr(cls, newName, getattr(cls, oldName))
            closure = lambda newName: lambda self, *args: _callStoreFirst(self,
                    newName, *args)
            setattr(cls, oldName, closure(newName))

        # We do not call postSetup when job_stream requests it.  This is because
        # our jobs must be set up in each thread, so we defer until it is called
        # in a thread.
        cls.mPostSetup = cls.postSetup
        cls.postSetup = lambda self: True


    def postSetup(self):
        """Called when self.config is set and the Job is fully ready for work,
        but before any work is accepted."""
        pass


    def handleInit(self, store):
        """Called when a reduction is started.  Store is a python object that
        should be modified to remember information between invocations."""


    def handleAdd(self, store, work):
        """Called when new work arrives at the Reducer."""
        raise NotImplementedError()


    def handleJoin(self, store, other):
        """Called to merge two stores from the same Reducer."""
        raise NotImplementedError()


    def handleDone(self, store):
        """Called when the reduction is finished.  The reduction will be marked
        as unfinished if a recur() happens."""
        raise NotImplementedError()



class Frame(_j.Frame):
    """Base class for a Frame.  A Frame is a special type of reducer that
    performs some special behavior based on the work that begins the reduction.
    Typically this is used for checking termination conditions in a recurring
    algorithm:

    import job_stream
    class AddAb(job_stream.Job):
        def handleWork(self, w):
            self.emit(w + 'Ab')
    class MakeAtLeastTenLetters(job_stream.Frame):
        def handleFirst(self, store, w):
            store.word = w
        def handleNext(self, store, w):
            store.word = w
        def handleDone(self, store):
            if len(store.word) < 10:
                self.recur(store.word)
            else:
                self.emit(store.word)

    job_stream.work = [ 'abracadabra', 'Hey', 'Apples' ]
    # This'll print out the unmodified abracadabra, add two Ab's to Apples, and
    # four Ab's to Hey
    job_stream.run({
            'jobs': [ {
                'frame': MakeAtLeastTenLetters,
                'jobs': [ AddAb ]
            } ]
    })
    """
    class __metaclass__(type(_j.Frame)):
        def __init__(cls, name, bases, attrs):
            # Derived hierarchical name, use that in config
            fullname = _hierarchicalName(cls, name)

            # Metaclasses are called for their first rendition as well, so...
            if fullname == 'job_stream.Frame':
                return

            _classesToPatch.append(cls)
            _j.registerFrame(fullname, cls)


    USE_MULTIPROCESSING = Job.USE_MULTIPROCESSING
    USE_MULTIPROCESSING_doc = Job.USE_MULTIPROCESSING_doc


    @classmethod
    def _patchForMultiprocessing(cls):
        if hasattr(cls, '_MULTIPROCESSING_PATCHED'):
            return

        cls._MULTIPROCESSING_PATCHED = True
        def newInit(self):
            super(cls, self).__init__()
            _initMultiprocessingPool()
            self.id = _localJobId[0]
            _localJobId[0] += 1
        cls.__init__ = newInit

        for oldName in [ 'handleFirst', 'handleNext', 'handleDone' ]:
            newName = 'm' + oldName[0].upper() + oldName[1:]
            setattr(cls, newName, getattr(cls, oldName))
            closure = lambda newName: lambda self, *args: _callStoreFirst(self,
                    newName, *args)
            setattr(cls, oldName, closure(newName))

        # We do not call postSetup when job_stream requests it.  This is because
        # our jobs must be set up in each thread, so we defer until it is called
        # in a thread.
        cls.mPostSetup = cls.postSetup
        cls.postSetup = lambda self: True


    def handleFirst(self, store, work):
        """Called for the first work, which starts a reduction.  Store is an
        empty Object() to which this method may assign attributes."""
        raise NotImplementedError()


    def handleNext(self, store, work):
        """Called when finished work arrives at the Frame."""
        raise NotImplementedError()


    def handleDone(self, store):
        """Called when the reduction is finished.  The reduction will be marked
        as unfinished if a recur() happens."""
        raise NotImplementedError()


    def postSetup(self):
        """Called when self.config is set and the Frame is fully ready for work,
        but before any work is accepted."""


def _convertDictToYaml(c):
    levels = [ { 'type': dict, 'vals': c.iteritems() } ]
    result = []
    def cueLine():
        result.append("  " * (len(levels) - 1))
    while levels:
        try:
            val = levels[-1]['vals'].next()
        except StopIteration:
            levels.pop()
            continue

        cueLine()
        if levels[-1]['type'] == dict:
            key, dval = val
            result.append(key)
            result.append(": ")
            val = dval
        elif levels[-1]['type'] == list:
            result.append("- ")

        # Now, the value part
        if isinstance(val, dict):
            levels.append({ 'type': dict, 'vals': val.iteritems() })
        elif isinstance(val, list):
            if len(val) == 0:
                result.append("[]")
            else:
                levels.append({ 'type': list, 'vals': iter(val) })
        elif isinstance(val, (int, float, basestring)):
            result.append(str(val))
        elif issubclass(val, (Frame, Job, Reducer)):
            result.append(_hierarchicalName(val))
        else:
            raise ValueError("Unrecognized YAML object: {}: {}".format(key,
                    val))

        result.append("\n")

    result = ''.join(result)
    return result


checkpointInfo = _j.checkpointInfo


def getRank():
    """Returns the rank (integer index) of this processor.  Typically, this
    value is checked against 0 for work that should only happen once, e.g.
    init code."""
    return _j.getRank()


def invoke(progAndArgs, transientErrors = [], maxRetries = 20):
    """Since it can be difficult to launch some programs from an MPI distributed
    application, job_stream provides invoke functionality to safely launch an
    external program (launching an application such as Xyce, for instance, can
    cause problems if the environment variables are not doctored appropriately).

    progAndArgs: list, [ 'path/to/file', *args ]

    transientErrors: list of strings, if any of these strings are found in the
            stderr of the program, then any non-zero return code is considered
            a transient error and the application will be re-launched up to
            maxRetries times.

            Note that "No child processes" is automatically handled as
            transient.

    maxRetries: The maximum number of times to run the application if there are
            transient errors.  Only the final (successful) results are returned.

    Returns: (contents of stdout, contents of stderr)
    """
    return _j.invoke(progAndArgs, transientErrors, maxRetries)


def run(configDictOrPath, **kwargs):
    """Runs the given YAML file or config dictionary.

    Acceptable kwargs:
        checkpointFile - (string) The file to use for checkpoint / restore
        checkpointInterval - (float) The time between the completion of one
                checkpoint and the starting of the next, in seconds.
        checkpointSyncInterval - (float) The time between all processors
                thinking they're ready to checkpoint and the actual checkpoint.
        handleResult - (callable) The default is to print out repr(result).  If
                specified, this function will be called instead with the output
                work as an argument.  Note that this goes outside of checkpointing!
                If you are saving work into an array, for example, and want to be
                checkpoint-safe, this method MUST save what it needs to file.
    """
    if isinstance(configDictOrPath, basestring):
        # Path to file
        config = open(configDictOrPath).read()
    elif isinstance(configDictOrPath, dict):
        config = _convertDictToYaml(configDictOrPath)
    else:
        raise ValueError("configDictOrPath was not dict or filename!")

    for cls in reversed(_classesToPatch):
        if cls.USE_MULTIPROCESSING:
            cls._patchForMultiprocessing()

    if 'handleResult' not in kwargs:
        def handleResult(r):
            """Process an output work.  Note that this function is responsible for
            checkpointing!
            """
            print(repr(r))
    else:
        handleResult = kwargs.pop('handleResult')

    try:
        _j.runProcessor(config, list(work), handleResult, **kwargs)
    finally:
        # Close our multiprocessing pool; especially in the interpreter, the
        # pool must be launched AFTER all classes are defined.  So if we define
        # a class in between invocations of run(), we still want them to work
        if _pool[0] is not None:
            p = _pool[0]
            _pool[0] = None
            p.terminate()
            p.join()

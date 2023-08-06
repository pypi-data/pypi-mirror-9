"""Models for call graphs and frames.

"""
from appdynamics.lib import internal_frame


class Call(object):
    """Represents a call made by the program.

    Attributes
    ----------
    frame : FrameInfo
    time_taken_ms : int
    parent : Call or None
    children : iterable[Call]
    exit_calls : set[appdynamics.agent.models.exitcalls.ExitCall]

    """
    __slots__ = ('frame', '_time_taken_ms', 'parent', 'children', 'exit_calls')

    def __init__(self, frame):
        super(Call, self).__init__()
        self.frame = frame
        self.parent = None
        self.children = []
        self.exit_calls = set()
        self._time_taken_ms = 0.0

    @property
    def time_taken_ms(self):
        return int(round(self._time_taken_ms))


class SampleData(object):
    """Represents the data associated with profiler samples for a BT.

    """
    __slots__ = ('samples', 'sample_time', 'sample_last_time', 'greenlet_ref', 'thread_id', 'frame_cache')

    def __init__(self, thread_id, greenlet_ref):
        super(SampleData, self).__init__()
        self.samples = []
        self.sample_time = 0
        self.sample_last_time = None
        self.thread_id = thread_id
        self.greenlet_ref = greenlet_ref
        self.frame_cache = {}

    @property
    def time_per_sample(self):
        if self.samples:
            return float(self.sample_time) / len(self.samples)
        else:
            return 0

    def take(self, frames, now, exit_call):
        # if self.greenlet_ref:
        #     ctx = self.greenlet_ref()

        #     if ctx:
        #         leaf = ctx.gr_frame
        #     else:
        #         leaf = frames.get(self.thread_id, None)
        # else:

        leaf = frames.get(self.thread_id, None)

        if leaf is None:
            return

        stack = tuple(FrameIterator(leaf, self.frame_cache))
        stack_with_exit = (stack, exit_call)
        self.samples.append(stack_with_exit)
        self.sample_time += now - self.sample_last_time
        self.sample_last_time = now


class FrameInfo(object):
    """Copy of the important info from a Python frame.

    """
    __slots__ = ('class_name', 'name', 'filename', 'lineno', 'internal', '_hash')

    def __init__(self, frame):
        super(FrameInfo, self).__init__()
        code = frame.f_code

        try:
            self.class_name = frame.f_locals['self'].__class__.__name__
        except:
            self.class_name = None

        self._hash = frame_hash(frame)
        self.name = code.co_name
        self.filename = code.co_filename
        self.lineno = code.co_firstlineno
        self.internal = internal_frame(frame.f_code.co_filename)

    def __hash__(self):
        return self._hash

    def __eq__(self, rhs):
        try:
            return (
                self.name == rhs.name and
                self.filename == rhs.filename and
                self.lineno == rhs.lineno)
        except:
            return False


def frame_hash(f):
    code = f.f_code
    key = (code.co_name, code.co_filename, code.co_firstlineno)
    return hash(key)


class FrameIterator(object):
    """An iterator over Python frames.

    Given a starting frame, this will return that frame followed by its calling
    frame, then the calling frame's caller, and so on back to the outer-most
    frame.

    """
    __slots__ = ('next_frame', 'frame_cache')

    def __init__(self, frame, frame_cache):
        super(FrameIterator, self).__init__()
        self.frame_cache = frame_cache
        self.next_frame = frame

    def __iter__(self):
        return self

    def __next__(self):  # Py3 iterator protocol
        if self.next_frame is None:
            raise StopIteration

        frame = self.next_frame
        self.next_frame = frame.f_back

        try:
            return self.frame_cache[frame]
        except KeyError:
            frame_info = FrameInfo(frame)
            self.frame_cache[frame] = frame_info
            return frame_info

    next = __next__  # Py2 iterator protocol


def make_call_graph(sample_data, total_time_taken_ms, include_internal_frames=False):
    """Create a call graph from a iterable of samples.

    Each sample is an iterable of FrameInfo instances in the
    order returned by FrameIterator (that is, starting from the
    leaf up to the root).

    Parameters
    ----------
    sample_data : appdynamics.agent.models.callgraph.SampleData
    total_time_taken_ms : int
        The precise time taken in the business transaction

    Other Parameters
    ----------------
    include_internal_frames : bool, optional

    Returns
    -------
    root : Call
        The call graph

    """
    root = Call(None)  # Always have a common root node.

    samples = sample_data.samples
    tps = sample_data.time_per_sample
    calls_cache = {}

    def get_call(stack):
        try:
            return calls_cache[stack]
        except:
            call = Call(stack[0])
            call.parent = calls_cache[stack[1:]] if len(stack) > 1 else root
            call.parent.children.append(call)

            calls_cache[stack] = call
            return call

    calls_with_exit_calls = set()

    for sample, exit_call in samples:
        if not include_internal_frames:
            sample = filter(lambda f: not f.internal, sample)

        if not sample:  # Nothing to do
            continue

        depth = len(sample)
        calls = [get_call(sample[-i:]) for i in xrange(1, depth + 1)]

        if calls and exit_call:
            for call in calls:  # Find the call the exit call occurred in.
                if call.frame == exit_call.caller:
                    assign_to = call
                    break
            else:  # The exit call's frame wasn't in the stack.
                assign_to = calls[-1]  # So attach it to the leaf.

            assign_to.exit_calls.add(exit_call)
            calls_with_exit_calls.add(assign_to)

        for call in calls:
            call._time_taken_ms += tps

    fix_exit_call_timings(calls_with_exit_calls)
    root._time_taken_ms = max(total_time_taken_ms, sum(node._time_taken_ms for node in root.children))
    return root


def fix_exit_call_timings(calls):
    """Fix frames where the exit call times exceed the sampled time.

    Since our call graph timings are gathered from a sampler, it's possible
    that we under-sample a frame. This is normally hard to see and relatively
    benign. But in the case of a frame with an exit call, the exit call
    timing is "exact", while the frame time is sampled, and it's possible for
    the user visible exit call timing to exceed the sampled frame time.

    This is confusing for the user and wrong. So when we have better info,
    and we can detect that we under-sampled, make the frame at least as long
    as the sum of the times spent in its exit calls.

    Parameters
    ----------
    calls : iterable[Call]

    """
    for call in calls:
        exit_time_ms = sum(exit_call.time_taken_ms for exit_call in call.exit_calls)
        dt = exit_time_ms - call.time_taken_ms

        if dt > 0:  # The frame was obviously under-sampled.
            while call:  # Give it and its ancestors the extra time.
                call._time_taken_ms += dt
                call = call.parent

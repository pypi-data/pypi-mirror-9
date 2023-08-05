#! /usr/bin/env python
"""
frameset - A set-like object representing a frame range for fileseq.
"""

from collections import Set, Sequence
from fileseq.utils import xfrange, unique, pad
from fileseq.constants import PAD_MAP, FRANGE_RE, PAD_RE
from fileseq.exceptions import ParseException

class FrameSet(Set):
    """
    A FrameSet is an immutable representation of the ordered, unique set of
    frames in a given frame range.

    The frame range can be expressed in the following ways:
        1-5
        1-5,10-20
        1-100x5 (every fifth frame)
        1-100y5 (opposite of above, fills in missing frames)
        1-100:4 (same as 1-100x4,1-100x3,1-100x2,1-100)

    A FrameSet is effectively an ordered frozenset, with FrameSet-returning
    versions of frozenset methods:
        >>> FrameSet('1-5').union(FrameSet('5-10')
        FrameSet('1-10')
        >>> FrameSet('1-5').intersection(FrameSet('5-10')
        FrameSet('5')

    Because a FrameSet is hashable, it can be used as the key to a dictionary:
        >>> {FrameSet('1-20'): 'good'}

    Caveats:
        1: all frozenset operations return a normalized FrameSet: internal
        frames are in numerically increasing order
        2: equality is based on the contents and order, NOT the frame range
        string (there are a finite, but potentially
        extremely large, number of strings that can represent any given range,
        only a "best guess" can be made)
        3: human-created frame ranges (ie 1-100x5) will be reduced to the
        actual internal frames (ie 1-96x5)
    """

    __slots__ = ('_frange', '_items', '_order')

    def __new__(cls, *args, **kwargs):
        """
        Initialize the FrameSet object.
        :param frange: the frame range as a str (ie "1-100x5")
        :return: the FrameSet instance
        :raises: fileseq.ParseException if the frame range (or a portion of it
        could not be parsed
        """
        self = super(cls, FrameSet).__new__(cls, *args, **kwargs)
        return self


    def __init__(self, frange):
        """
        Initialize the FrameSet object.
        :param frange: the frame range as a str (ie "1-100x5")
        :return: None
        :raises: fileseq.ParseException if the frame range (or a portion of it
        could not be parsed
        """

        # if the user provides anything but a string, short-circuit the build
        if not isinstance(frange, basestring):
            # we may already know frange, items, and contents; this will
            # allow our own code to get back the instance before the expensive
            # calculation of items and order
            if frange is None:
                return
            # if it's apparently a FrameSet already, short-circuit the build
            elif set(dir(frange)).issuperset(self.__slots__):
                for attr in self.__slots__:
                    setattr(self, attr, getattr(frange, attr))
                return
            # if it's inherently disordered, sort and build
            elif isinstance(frange, Set):
                self._items = frozenset(frange)
                self._order = tuple(sorted(self._items))
                self._frange = FrameSet.framesToFrameRange(
                    self._order, sort=False, compress=False)
                return
            # if it's ordered, find unique and build
            elif isinstance(frange, Sequence):
                items = set()
                order = unique(items, frange)
                self._order = tuple(order)
                self._items = frozenset(items)
                self._frange = FrameSet.framesToFrameRange(
                    self._order, sort=False, compress=False)
                return
            # in all other cases, cast to a string
            else:
                try:
                    frange = str(frange)
                except Exception as err:
                    msg = 'Could not parse "{0}": cast to string raised: {1}'
                    raise ParseException(msg.format(frange, err))

        # we're willing to trim padding characters from consideration
        # this translation is orders of magnitude faster than prior method
        self._frange = str(frange).translate(None, ''.join(PAD_MAP.keys()))

        # because we're acting like a set, we need to support the empty set
        if not self._frange:
            self._items = frozenset()
            self._order = tuple()
            return

        # build the mutable stores, then cast to immutable for storage
        items = set()
        order = []

        for part in self._frange.split(","):
            # this is to deal with leading / trailing commas
            if not part:
                continue
            # parse the partial range
            start, end, modifier, chunk = FrameSet._parse_frange_part(part)
            # handle batched frames (1-100x5)
            if modifier == 'x':
                frames = xfrange(start, end, chunk)
                frames = [f for f in frames if f not in items]
                order.extend(frames)
                items.update(frames)
            # handle staggered frames (1-100:5)
            elif modifier == ':':
                for stagger in xrange(chunk, 0, -1):
                    frames = xfrange(start, end, stagger)
                    frames = [f for f in frames if f not in items]
                    order.extend(frames)
                    items.update(frames)
            # handle filled frames (1-100y5)
            elif modifier == 'y':
                not_good = frozenset(xfrange(start, end, chunk))
                frames = xfrange(start, end, 1)
                frames = (f for f in frames if f not in not_good)
                frames = [f for f in frames if f not in items]
                order.extend(frames)
                items.update(frames)
            # handle full ranges and single frames
            else:
                frames = xfrange(start, end, 1 if start < end else -1)
                frames = [f for f in frames if f not in items]
                order.extend(frames)
                items.update(frames)

        # lock the results into immutable internals
        # this allows for hashing and fast equality checking
        self._items = frozenset(items)
        self._order = tuple(order)

    @property
    def frange(self):
        """
        Read-only access to the frame range used to create this FrameSet.
        :return: frozenset
        """
        return self._frange

    @property
    def items(self):
        """
        Read-only access to the unique frames that form this FrameSet.
        :return: frozenset
        """
        return self._items

    @property
    def order(self):
        """
        Read-only access to the ordered frames that form this FrameSet.
        :return: tuple
        """
        return self._order

    @classmethod
    def from_iterable(cls, frames, sort=False):
        """
        Build a FrameSet from an iterable of frames.
        :param frames: an iterable object containing frames as integers
        :param sort: True to sort frames before creation, default is False
        :return: fileseq.FrameSet
        """
        return FrameSet(sorted(frames) if sort else frames)

    @classmethod
    def _cast_to_frameset(cls, other):
        """
        Private method to simplify comparison operations.
        :param other: the FrameSet, set, frozenset, or iterable to be compared
        :return: a FrameSet (or NotImplemented if a comparison is impossible)
        """
        if isinstance(other, FrameSet):
            return other
        try:
            return FrameSet(other)
        except Exception:
            return NotImplemented

    def index(self, frame):
        """
        Return the index of the given frame number within the FrameSet.
        :param frame: the frame int to find the index for
        :return: int
        :raises: ValueError if frame is not in self
        """
        return self.order.index(frame)

    def frame(self, index):
        """
        Return the frame at the given index.
        :param index: the index int to find the frame for
        :return: int
        :raises: IndexError if index is out of bounds
        """
        return self.order[index]

    def hasFrame(self, frame):
        """
        Check if the FrameSet contains the frame.
        :param frame: the frame int to search for
        :return: bool
        """
        return frame in self

    def start(self):
        """
        The first frame in the FrameSet.
        :return: int
        :raises: IndexError (with the empty FrameSet)
        """
        return self.order[0]

    def end(self):
        """
        The last frame in the FrameSet.
        :return: int
        :raises: IndexError (with the empty FrameSet)
        """
        return self.order[-1]

    def frameRange(self, zfill=0):
        """
        Return the frame range used to create this FrameSet, padded if desired.
        For example:
            >>> FrameSet('1-100').frameRange()
            '1-100'
            >>> FrameSet('1-100').frameRange(5)
            '00001-00100'
        :param zfill: the width int to use to zero-pad the frame range string
        :return: str
        """
        return FrameSet.padFrameRange(self.frange, zfill)

    def invertedFrameRange(self, zfill=0):
        """
        Return the inverse of the FrameSet's frame range, padded if desired.
        The inverse is every frame within the full extents of the range:
            >>> FrameSet('1-100x2').invertedFrameRange()
            '2-98x2'
            >>> FrameSet('1-100x2').invertedFrameRange(5)
            '00002-00098x2'
        :param zfill: the width int to use to zero-pad the frame range string
        :return: str
        """
        result = []
        frames = sorted(self.items)
        for idx, frame in enumerate(frames[:-1]):
            next_frame = frames[idx + 1]
            if next_frame - frame != 1:
                result += xrange(frame + 1, next_frame)
        if not result:
            return ''
        return FrameSet.framesToFrameRange(
            result, zfill=zfill, sort=False, compress=False)

    def normalize(self):
        """
        Returns a new normalized (sorted and compacted) FrameSet.
        :return: FrameSet
        """
        return FrameSet(FrameSet.framesToFrameRange(
            self.items, sort=True, compress=False))

    def __getstate__(self):
        """
        Allows for serialization to a pickled FrameSet.
        :return: tuple (frame range string, )
        """
        # we have to special-case the empty FrameSet, because of a quirk in
        # Python where __setstate__ will not be called if the return value of
        # bool(__getstate__) == False.  A tuple with ('',) will return True.
        return (self.frange, )

    def __setstate__(self, state):
        """
        Allows for de-serialization from a pickled FrameSet.
        :param state: tuple (string/dict for backwards compatibility)
        :return: None
        :raises: ValueError if state is not an appropriate type
        """
        if isinstance(state, tuple):
            # this is to allow unpickling of "3rd generation" FrameSets,
            # which are immutable and may be empty.
            self.__init__(state[0])
        elif isinstance(state, basestring):
            # this is to allow unpickling of "2nd generation" FrameSets,
            # which were mutable and could not be empty.
            self.__init__(state)
        elif isinstance(state, dict):
            # this is to allow unpickling of "1st generation" FrameSets,
            # when the full __dict__ was stored
            if '__frange' in state and '__set' in state and '__list' in state:
                self._frange = state['__frange']
                self._items = frozenset(state['__set'])
                self._order = tuple(state['__list'])
            else:
                for k in self.__slots__:
                    setattr(self, k, state[k])
        else:
            msg = "Unrecognized state data from which to deserialize FrameSet"
            raise ValueError(msg)

    def __getitem__(self, index):
        """
        Allows indexing into the ordered frames of this FrameSet.
        :param index: the index int to retrieve
        :return: int
        :raises: IndexError if index is out of bounds
        """
        return self.order[index]

    def __len__(self):
        """
        Returns the length of the ordered frames of this FrameSet.
        :return: int
        """
        return len(self.order)

    def __str__(self):
        """
        Returns the frame range string of this FrameSet.
        :return: str
        """
        return self.frange

    def __repr__(self):
        """
        Returns a long-form representation of this FrameSet.
        :return: str
        """
        return '{0}("{1}")'.format(self.__class__.__name__, self.frange)

    def __iter__(self):
        """
        Allows for iteration over the ordered frames of this FrameSet.
        :return: generator
        """
        return (i for i in self.order)

    def __reversed__(self):
        """
        Allows for reversed iteration over the ordered frames of this FrameSet.
        :return: generator
        """
        return (i for i in reversed(self.order))

    def __contains__(self, item):
        """
        Check if item is a member of this FrameSet.
        :param item: the frame int to check for
        :return: bool
        """
        return item in self.items

    def __hash__(self):
        """
        Builds the hash of this FrameSet for equality checking and to allow use
        as a dictionary key.
        :return: int
        """
        return hash(self.frange) | hash(self.items) | hash(self.order)

    def __lt__(self, other):
        """
        Check if self < other via a comparison of the contents. If other is not
        a FrameSet, but is a set, frozenset, or is iterable, it will be cast to
        a FrameSet.
        Note: a FrameSet is less than other if the set of its contents are
        less, OR if the contents are equal but the order of the items is less.
        For example:
            >>> FrameSet("1-5") < FrameSet("5-1")
            True # same contents, but (1,2,3,4,5) sorts below (5,4,3,2,1)

        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items < other.items or (
            self.items == other.items and self.order < other.order)

    def __le__(self, other):
        """
        Check if self <= other via a comparison of the contents. If other is
        not a FrameSet, but is a set, frozenset, or is iterable, it will be
        cast to a FrameSet.
        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items <= other.items

    def __eq__(self, other):
        """
        Check if self == other via a comparison of the hash of their contents.
        If other is not a FrameSet, but is a set, frozenset, or is iterable, it
        will be cast to a FrameSet.
        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        if not isinstance(other, FrameSet):
            if not hasattr(other, '__iter__'):
                return NotImplemented
            other = self.from_iterable(other)
        this = hash(self.items) | hash(self.order)
        that = hash(other.items) | hash(other.order)
        return this == that

    def __ne__(self, other):
        """
        Check if self != other via a comparison of the hash of their contents.
        If other is not a FrameSet, but is a set, frozenset, or is iterable, it
        will be cast to a FrameSet.
        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        is_equals = self == other
        if is_equals != NotImplemented:
            return not is_equals
        return is_equals

    def __ge__(self, other):
        """
        Check if self >= other via a comparison of the contents. If other is
        not a FrameSet, but is a set, frozenset, or is iterable, it will be
        cast to a FrameSet.
        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items >= other.items

    def __gt__(self, other):
        """
        Check if self > other via a comparison of the contents. If other is not
        a FrameSet, but is a set, frozenset, or is iterable, it will be cast to
        a FrameSet.
        Note: a FrameSet is greater than other if the set of its contents are
        greater, OR if the contents are equal but the order is greater.
        For example:
            >>> FrameSet("1-5") > FrameSet("5-1")
            False # same contents, but (1,2,3,4,5) sorts below (5,4,3,2,1)

        :param other: FrameSet (or an object that can be cast to one)
        :return: bool (NotImplemented if other fails convert to a FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items > other.items or (
            self.items == other.items and self.order > other.order)

    def __and__(self, other):
        """
        Overloads the & operator: returns a new FrameSet that holds only the
        frames self and other have in common.
        Note: the order of operations is irrelevant:
            self & other) == (other & self)
        :param other: FrameSet
        :return: FrameSet (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.from_iterable(self.items & other.items, sort=True)

    __rand__ = __and__

    def __sub__(self, other):
        """
        Overloads the - operator: returns a new FrameSet that holds only the
        frames of self that are not in other.
        Note: this is for left-hand subtraction (self - other).
        :param other: FrameSet
        :return: FrameSet (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.from_iterable(self.items - other.items, sort=True)

    def __rsub__(self, other):
        """
        Overloads the - operator: returns a new FrameSet that holds only the
        frames of other that are not in self.
        Note: this is for right-hand subtraction (other - self).
        :param other: FrameSet
        :return: FrameSet (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.from_iterable(other.items - self.items, sort=True)

    def __or__(self, other):
        """
        Overloads the | operator: returns a new FrameSet that holds all the
        frames in self, other, or both.
        Note: the order of operations is irrelevant:
            (self | other) == (other | self)
        :param other: FrameSet
        :return: FrameSet (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.from_iterable(self.items | other.items, sort=True)

    __ror__ = __or__

    def __xor__(self, other):
        """
        Overloads the ^ operator: returns a new FrameSet that holds all the
        frames in self or other but not both.
        Note: the order of operations is irrelevant:
            (self ^ other) == (other ^ self)
        :param other: FrameSet
        :return: FrameSet (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.from_iterable(self.items ^ other.items, sort=True)

    __rxor__ = __xor__

    def isdisjoint(self, other):
        """
        Check if the contents of self have no common intersection with the
        contents of other.
        :param other: FrameSet
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items.isdisjoint(other.items)

    def issubset(self, other):
        """
        Check if the contents of self is a subset of the contents of other.
        :param other: FrameSet
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items <= other.items

    def issuperset(self, other):
        """
        Check if the contents of self is a superset of the contents of other.
        :param other: FrameSet
        :return: bool (NotImplemented if other fails convert to FrameSet)
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        return self.items >= other.items

    def union(self, *other):
        """
        Returns new FrameSet with elements from self and elements of other(s).
        :param other: FrameSet(s) or other object(s) that can cast to FrameSet
        :return: FrameSet
        """
        from_frozenset = self.items.union(*map(set, other))
        return self.from_iterable(from_frozenset, sort=True)

    def intersection(self, *other):
        """
        Returns new FrameSet with elements common to self and other(s).
        :param other: FrameSet(s) or other object(s) that can cast to FrameSet
        :return: FrameSet
        """
        from_frozenset = self.items.intersection(*map(set, other))
        return self.from_iterable(from_frozenset, sort=True)

    def difference(self, *other):
        """
        Returns new FrameSet with elements in self but not in other(s).
        :param other: FrameSet(s) or other object(s) that can cast to FrameSet
        :return: FrameSet
        """
        from_frozenset = self.items.difference(*map(set, other))
        return self.from_iterable(from_frozenset, sort=True)

    def symmetric_difference(self, other):
        """
        Returns new FrameSet that contains all the elements in either self or
        other, but not both.
        :param other: FrameSet
        :return: FrameSet
        """
        other = self._cast_to_frameset(other)
        if other is NotImplemented:
            return NotImplemented
        from_frozenset = self.items.symmetric_difference(other.items)
        return self.from_iterable(from_frozenset, sort=True)

    def copy(self):
        """
        Returns a shallow copy of this FrameSet.
        :return: FrameSet
        """
        return FrameSet(str(self))

    @staticmethod
    def isFrameRange(frange):
        """
        Return true of the given string is a frame range.  Any padding
        characters, such as '#' and '@' are ignored.
        :param frange: a frame range (str) to test
        :return: bool
        """
        # we're willing to trim padding characters from consideration
        # this translation is orders of magnitude faster than prior method
        frange = str(frange).translate(None, ''.join(PAD_MAP.keys()))
        if not frange:
            return True
        for part in frange.split(','):
            if not part:
                continue
            try:
                FrameSet._parse_frange_part(part)
            except ParseException:
                return False
        return True

    @staticmethod
    def padFrameRange(frange, zfill):
        """
        Return the zero-padded version of the frame range string.
        :param frange: a frame range (str) to test
        :return: str
        """
        def _do_pad(match):
            """
            Substitutes padded for unpadded frames.
            """
            result = list(match.groups())
            result[1] = pad(result[1], zfill)
            if result[4]:
                result[4] = pad(result[4], zfill)
            return ''.join((i for i in result if i))
        return PAD_RE.sub(_do_pad, frange)

    @staticmethod
    def _parse_frange_part(frange):
        """
        Internal method: parse a discreet frame range part.
        :param frange: single part of a frame range as a str (ie "1-100x5")
        :return: tuple (start, end, modifier, chunk)
        :raises: fileseq.ParseException if the frame range can not be parsed
        """
        match = FRANGE_RE.match(frange)
        if not match:
            msg = 'Could not parse "{0}": did not match {1}'
            raise ParseException(msg.format(frange, FRANGE_RE.pattern))
        start, end, modifier, chunk = match.groups()
        start = int(start)
        end = int(end) if end is not None else start
        chunk = abs(int(chunk)) if chunk is not None else 1
        # a zero chunk is just plain illogical
        if chunk == 0:
            msg = 'Could not parse "{0}": chunk cannot be 0'
            raise ParseException(msg.format(frange))
        return start, end, modifier, chunk

    @staticmethod
    def _build_frange_part(start, stop, stride, zfill=0):
        """
        Private method: builds a proper and padded FrameRange string.
        :param start: first frame (int)
        :param stop: last frame (int)
        :param stride: increment (int)
        :param zfill: width for zero padding (int)
        :return: str
        """
        if stop is None:
            return ''
        pad_start = pad(start, zfill)
        pad_stop = pad(stop, zfill)
        if stride is None or start == stop:
            return '{0}'.format(pad_start)
        elif abs(stride) == 1:
            return '{0}-{1}'.format(pad_start, pad_stop)
        else:
            return '{0}-{1}x{2}'.format(pad_start, pad_stop, stride)

    @staticmethod
    def framesToFrameRanges(frames, zfill=0):
        """
        Converts a sequence of frames to a series of padded FrameRanges.
        :param frames: sequence of frames to process (iter)
        :param zfill: width for zero padding (int)
        :return: generator
        """
        _build = FrameSet._build_frange_part
        curr_start = None
        curr_stride = None
        curr_frame = None
        last_frame = None
        curr_count = 0
        for curr_frame in frames:
            if curr_start is None:
                curr_start = curr_frame
                last_frame = curr_frame
                curr_count += 1
                continue
            if curr_stride is None:
                curr_stride = abs(curr_frame-curr_start)
            new_stride = abs(curr_frame-last_frame)
            if curr_stride == new_stride:
                last_frame = curr_frame
                curr_count += 1
            elif curr_count == 2:
                yield _build(curr_start, curr_start, None, zfill)
                curr_start = last_frame
                curr_stride = new_stride
                last_frame = curr_frame
            else:
                yield _build(curr_start, last_frame, curr_stride, zfill)
                curr_stride = None
                curr_start = curr_frame
                last_frame = curr_frame
                curr_count = 1
        if curr_count == 2:
            yield _build(curr_start, curr_start, None, zfill)
            yield _build(curr_frame, curr_frame, None, zfill)
        else:
            yield _build(curr_start, curr_frame, curr_stride, zfill)

    @staticmethod
    def framesToFrameRange(frames, sort=True, zfill=0, compress=False):
        """
        Converts an iterator of frames into a FrameRange.
        :param frames: sequence of frames to process (iter)
        :param sort: sort the sequence before processing (bool)
        :param zfill: width for zero padding (int)
        :param compress: remove any duplicates before processing (bool)
        :return: str
        """
        if compress:
            frames = unique(set(), frames)
        frames = list(frames)
        if not frames:
            return ''
        if len(frames) == 1:
            return pad(frames[0], zfill)
        if sort:
            frames.sort()
        return ','.join(FrameSet.framesToFrameRanges(frames, zfill))

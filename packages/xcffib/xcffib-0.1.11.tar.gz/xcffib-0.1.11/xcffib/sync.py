import xcffib
import struct
import six
MAJOR_VERSION = 3
MINOR_VERSION = 1
key = xcffib.ExtensionKey("SYNC")
_events = {}
_errors = {}
from . import xproto
class ALARMSTATE:
    Active = 0
    Inactive = 1
    Destroyed = 2
class TESTTYPE:
    PositiveTransition = 0
    NegativeTransition = 1
    PositiveComparison = 2
    NegativeComparison = 3
class VALUETYPE:
    Absolute = 0
    Relative = 1
class CA:
    Counter = 1 << 0
    ValueType = 1 << 1
    Value = 1 << 2
    TestType = 1 << 3
    Delta = 1 << 4
    Events = 1 << 5
class INT64(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.hi, self.lo = unpacker.unpack("iI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=iI", self.hi, self.lo))
        return buf.getvalue()
    fixed_size = 8
class SYSTEMCOUNTER(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.counter, = unpacker.unpack("I")
        self.resolution = INT64(unpacker)
        self.name_len, = unpacker.unpack("H")
        unpacker.pad("c")
        self.name = xcffib.List(unpacker, "c", self.name_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IH", self.counter, self.name_len))
        buf.write(self.resolution.pack())
        buf.write(xcffib.pack_list(self.name, "c"))
        return buf.getvalue()
class TRIGGER(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.counter, self.wait_type = unpacker.unpack("II")
        self.wait_value = INT64(unpacker)
        self.test_type, = unpacker.unpack("I")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=III", self.counter, self.wait_type, self.test_type))
        buf.write(self.wait_value.pack())
        return buf.getvalue()
class WAITCONDITION(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.trigger = TRIGGER(unpacker)
        unpacker.pad(INT64)
        self.event_threshold = INT64(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(self.trigger.pack())
        buf.write(self.event_threshold.pack())
        return buf.getvalue()
class CounterError(xcffib.Error):
    def __init__(self, unpacker):
        xcffib.Error.__init__(self, unpacker)
        base = unpacker.offset
        self.bad_counter, self.minor_opcode, self.major_opcode = unpacker.unpack("xx2xIHB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=x2xIHB", self.bad_counter, self.minor_opcode, self.major_opcode))
        return buf.getvalue()
BadCounter = CounterError
_errors[0] = CounterError
class AlarmError(xcffib.Error):
    def __init__(self, unpacker):
        xcffib.Error.__init__(self, unpacker)
        base = unpacker.offset
        self.bad_alarm, self.minor_opcode, self.major_opcode = unpacker.unpack("xx2xIHB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 1))
        buf.write(struct.pack("=x2xIHB", self.bad_alarm, self.minor_opcode, self.major_opcode))
        return buf.getvalue()
BadAlarm = AlarmError
_errors[1] = AlarmError
class InitializeReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xBB22x")
        self.bufsize = unpacker.offset - base
class InitializeCookie(xcffib.Cookie):
    reply_type = InitializeReply
class ListSystemCountersReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.counters_len, = unpacker.unpack("xx2x4xI20x")
        self.counters = xcffib.List(unpacker, SYSTEMCOUNTER, self.counters_len)
        self.bufsize = unpacker.offset - base
class ListSystemCountersCookie(xcffib.Cookie):
    reply_type = ListSystemCountersReply
class QueryCounterReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        unpacker.unpack("xx2x4x")
        self.counter_value = INT64(unpacker)
        self.bufsize = unpacker.offset - base
class QueryCounterCookie(xcffib.Cookie):
    reply_type = QueryCounterReply
class QueryAlarmReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        unpacker.unpack("xx2x4x")
        self.trigger = TRIGGER(unpacker)
        unpacker.pad(INT64)
        self.delta = INT64(unpacker)
        self.events, self.state = unpacker.unpack("BB2x")
        self.bufsize = unpacker.offset - base
class QueryAlarmCookie(xcffib.Cookie):
    reply_type = QueryAlarmReply
class GetPriorityReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.priority, = unpacker.unpack("xx2x4xi")
        self.bufsize = unpacker.offset - base
class GetPriorityCookie(xcffib.Cookie):
    reply_type = GetPriorityReply
class QueryFenceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.triggered, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class QueryFenceCookie(xcffib.Cookie):
    reply_type = QueryFenceReply
class CounterNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.kind, self.counter = unpacker.unpack("xB2xI")
        self.wait_value = INT64(unpacker)
        unpacker.pad(INT64)
        self.counter_value = INT64(unpacker)
        self.timestamp, self.count, self.destroyed = unpacker.unpack("IHBx")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=B2xIIHBx", self.kind, self.counter, self.timestamp, self.count, self.destroyed))
        buf.write(self.wait_value.pack())
        buf.write(self.counter_value.pack())
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[0] = CounterNotifyEvent
class AlarmNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.kind, self.alarm = unpacker.unpack("xB2xI")
        self.counter_value = INT64(unpacker)
        unpacker.pad(INT64)
        self.alarm_value = INT64(unpacker)
        self.timestamp, self.state = unpacker.unpack("IB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 1))
        buf.write(struct.pack("=B2xIIB3x", self.kind, self.alarm, self.timestamp, self.state))
        buf.write(self.counter_value.pack())
        buf.write(self.alarm_value.pack())
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[1] = AlarmNotifyEvent
class syncExtension(xcffib.Extension):
    def Initialize(self, desired_major_version, desired_minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xB", desired_major_version, desired_minor_version))
        return self.send_request(0, buf, InitializeCookie, is_checked=is_checked)
    def ListSystemCounters(self, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        return self.send_request(1, buf, ListSystemCountersCookie, is_checked=is_checked)
    def CreateCounter(self, id, initial_value, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", id))
        buf.write(initial_value.pack())
        return self.send_request(2, buf, is_checked=is_checked)
    def DestroyCounter(self, counter, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", counter))
        return self.send_request(6, buf, is_checked=is_checked)
    def QueryCounter(self, counter, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", counter))
        return self.send_request(5, buf, QueryCounterCookie, is_checked=is_checked)
    def Await(self, wait_list, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        buf.write(xcffib.pack_list(wait_list, WAITCONDITION))
        return self.send_request(7, buf, is_checked=is_checked)
    def ChangeCounter(self, counter, amount, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", counter))
        buf.write(amount.pack())
        return self.send_request(4, buf, is_checked=is_checked)
    def SetCounter(self, counter, value, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", counter))
        buf.write(value.pack())
        return self.send_request(3, buf, is_checked=is_checked)
    def CreateAlarm(self, id, value_mask, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", id, value_mask))
        return self.send_request(8, buf, is_checked=is_checked)
    def ChangeAlarm(self, id, value_mask, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", id, value_mask))
        return self.send_request(9, buf, is_checked=is_checked)
    def DestroyAlarm(self, alarm, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", alarm))
        return self.send_request(11, buf, is_checked=is_checked)
    def QueryAlarm(self, alarm, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", alarm))
        return self.send_request(10, buf, QueryAlarmCookie, is_checked=is_checked)
    def SetPriority(self, id, priority, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIi", id, priority))
        return self.send_request(12, buf, is_checked=is_checked)
    def GetPriority(self, id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", id))
        return self.send_request(13, buf, GetPriorityCookie, is_checked=is_checked)
    def CreateFence(self, drawable, fence, initially_triggered, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIB", drawable, fence, initially_triggered))
        return self.send_request(14, buf, is_checked=is_checked)
    def TriggerFence(self, fence, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", fence))
        return self.send_request(15, buf, is_checked=is_checked)
    def ResetFence(self, fence, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", fence))
        return self.send_request(16, buf, is_checked=is_checked)
    def DestroyFence(self, fence, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", fence))
        return self.send_request(17, buf, is_checked=is_checked)
    def QueryFence(self, fence, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", fence))
        return self.send_request(18, buf, QueryFenceCookie, is_checked=is_checked)
    def AwaitFence(self, fence_list, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        buf.write(xcffib.pack_list(fence_list, "I"))
        return self.send_request(19, buf, is_checked=is_checked)
xcffib._add_ext(key, syncExtension, _events, _errors)

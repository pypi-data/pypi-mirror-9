import xcffib
import struct
import six
MAJOR_VERSION = 1
MINOR_VERSION = 0
key = xcffib.ExtensionKey("Present")
_events = {}
_errors = {}
from . import xproto
from . import randr
from . import xfixes
from . import sync
class Event:
    ConfigureNotify = 0
    CompleteNotify = 1
    IdleNotify = 2
    RedirectNotify = 3
class EventMask:
    NoEvent = 0
    ConfigureNotify = 1 << 0
    CompleteNotify = 1 << 1
    IdleNotify = 1 << 2
    RedirectNotify = 1 << 3
class Option:
    _None = 0
    Async = 1 << 0
    Copy = 1 << 1
    UST = 1 << 2
class Capability:
    _None = 0
    Async = 1 << 0
    Fence = 1 << 1
    UST = 1 << 2
class CompleteKind:
    Pixmap = 0
    NotifyMSC = 1
class CompleteMode:
    Copy = 0
    Flip = 1
    Skip = 2
class Notify(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.window, self.serial = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.window, self.serial))
        return buf.getvalue()
    fixed_size = 8
class QueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xII")
        self.bufsize = unpacker.offset - base
class QueryVersionCookie(xcffib.Cookie):
    reply_type = QueryVersionReply
class QueryCapabilitiesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.capabilities, = unpacker.unpack("xx2x4xI")
        self.bufsize = unpacker.offset - base
class QueryCapabilitiesCookie(xcffib.Cookie):
    reply_type = QueryCapabilitiesReply
class GenericEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.extension, self.length, self.evtype, self.event = unpacker.unpack("xB2xIH2xI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=B2xIH2xI", self.extension, self.length, self.evtype, self.event))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[0] = GenericEvent
class ConfigureNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.event, self.window, self.x, self.y, self.width, self.height, self.off_x, self.off_y, self.pixmap_width, self.pixmap_height, self.pixmap_flags = unpacker.unpack("xx2x2xIIhhHHhhHHI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=x2x2xIIhhHHhhHHI", self.event, self.window, self.x, self.y, self.width, self.height, self.off_x, self.off_y, self.pixmap_width, self.pixmap_height, self.pixmap_flags))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[0] = ConfigureNotifyEvent
class CompleteNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.kind, self.mode, self.event, self.window, self.serial, self.ust, self.msc = unpacker.unpack("xB2xBIIIQQ")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 1))
        buf.write(struct.pack("=B2xBIIIQQ", self.kind, self.mode, self.event, self.window, self.serial, self.ust, self.msc))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[1] = CompleteNotifyEvent
class IdleNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.event, self.window, self.serial, self.pixmap, self.idle_fence = unpacker.unpack("xx2x2xIIIII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 2))
        buf.write(struct.pack("=x2x2xIIIII", self.event, self.window, self.serial, self.pixmap, self.idle_fence))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[2] = IdleNotifyEvent
class RedirectNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.update_window, self.event, self.event_window, self.window, self.pixmap, self.serial, self.valid_region, self.update_region = unpacker.unpack("xB2xxIIIIIII")
        self.valid_rect = xproto.RECTANGLE(unpacker)
        unpacker.pad(xproto.RECTANGLE)
        self.update_rect = xproto.RECTANGLE(unpacker)
        self.x_off, self.y_off, self.target_crtc, self.wait_fence, self.idle_fence, self.options, self.target_msc, self.divisor, self.remainder = unpacker.unpack("hhIIII4xQQQ")
        unpacker.pad(Notify)
        self.notifies = xcffib.List(unpacker, Notify, None)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 3))
        buf.write(struct.pack("=B2xxIIIIIIIhhIIII4xQQQ", self.update_window, self.event, self.event_window, self.window, self.pixmap, self.serial, self.valid_region, self.update_region, self.x_off, self.y_off, self.target_crtc, self.wait_fence, self.idle_fence, self.options, self.target_msc, self.divisor, self.remainder))
        buf.write(self.valid_rect.pack())
        buf.write(self.update_rect.pack())
        buf.write(xcffib.pack_list(self.notifies, Notify))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[3] = RedirectNotifyEvent
class presentExtension(xcffib.Extension):
    def QueryVersion(self, major_version, minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", major_version, minor_version))
        return self.send_request(0, buf, QueryVersionCookie, is_checked=is_checked)
    def Pixmap(self, window, pixmap, serial, valid, update, x_off, y_off, target_crtc, wait_fence, idle_fence, options, target_msc, divisor, remainder, notifies, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIIIIhhIIII4xQQQ", window, pixmap, serial, valid, update, x_off, y_off, target_crtc, wait_fence, idle_fence, options, target_msc, divisor, remainder))
        buf.write(xcffib.pack_list(notifies, Notify))
        return self.send_request(1, buf, is_checked=is_checked)
    def NotifyMSC(self, window, serial, target_msc, divisor, remainder, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII4xQQQ", window, serial, target_msc, divisor, remainder))
        return self.send_request(2, buf, is_checked=is_checked)
    def SelectInput(self, eid, window, event_mask, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIII", eid, window, event_mask))
        return self.send_request(3, buf, is_checked=is_checked)
    def QueryCapabilities(self, target, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", target))
        return self.send_request(4, buf, QueryCapabilitiesCookie, is_checked=is_checked)
xcffib._add_ext(key, presentExtension, _events, _errors)

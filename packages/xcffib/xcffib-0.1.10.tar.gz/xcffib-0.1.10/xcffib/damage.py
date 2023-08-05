import xcffib
import struct
import six
MAJOR_VERSION = 1
MINOR_VERSION = 1
key = xcffib.ExtensionKey("DAMAGE")
_events = {}
_errors = {}
from . import xproto
from . import xfixes
class ReportLevel:
    RawRectangles = 0
    DeltaRectangles = 1
    BoundingBox = 2
    NonEmpty = 3
class QueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xII16x")
        self.bufsize = unpacker.offset - base
class QueryVersionCookie(xcffib.Cookie):
    reply_type = QueryVersionReply
class NotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.level, self.drawable, self.damage, self.timestamp = unpacker.unpack("xB2xIII")
        self.area = xproto.RECTANGLE(unpacker)
        unpacker.pad(xproto.RECTANGLE)
        self.geometry = xproto.RECTANGLE(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=B2xIII", self.level, self.drawable, self.damage, self.timestamp))
        buf.write(self.area.pack())
        buf.write(self.geometry.pack())
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[0] = NotifyEvent
class damageExtension(xcffib.Extension):
    def QueryVersion(self, client_major_version, client_minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", client_major_version, client_minor_version))
        return self.send_request(0, buf, QueryVersionCookie, is_checked=is_checked)
    def Create(self, damage, drawable, level, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIB3x", damage, drawable, level))
        return self.send_request(1, buf, is_checked=is_checked)
    def Destroy(self, damage, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", damage))
        return self.send_request(2, buf, is_checked=is_checked)
    def Subtract(self, damage, repair, parts, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIII", damage, repair, parts))
        return self.send_request(3, buf, is_checked=is_checked)
    def Add(self, drawable, region, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", drawable, region))
        return self.send_request(4, buf, is_checked=is_checked)
xcffib._add_ext(key, damageExtension, _events, _errors)

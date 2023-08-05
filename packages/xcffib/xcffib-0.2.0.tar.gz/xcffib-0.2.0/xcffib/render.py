import xcffib
import struct
import six
MAJOR_VERSION = 0
MINOR_VERSION = 11
key = xcffib.ExtensionKey("RENDER")
_events = {}
_errors = {}
from . import xproto
class PictType:
    Indexed = 0
    Direct = 1
class Picture:
    _None = 0
class PictOp:
    Clear = 0
    Src = 1
    Dst = 2
    Over = 3
    OverReverse = 4
    In = 5
    InReverse = 6
    Out = 7
    OutReverse = 8
    Atop = 9
    AtopReverse = 10
    Xor = 11
    Add = 12
    Saturate = 13
    DisjointClear = 16
    DisjointSrc = 17
    DisjointDst = 18
    DisjointOver = 19
    DisjointOverReverse = 20
    DisjointIn = 21
    DisjointInReverse = 22
    DisjointOut = 23
    DisjointOutReverse = 24
    DisjointAtop = 25
    DisjointAtopReverse = 26
    DisjointXor = 27
    ConjointClear = 32
    ConjointSrc = 33
    ConjointDst = 34
    ConjointOver = 35
    ConjointOverReverse = 36
    ConjointIn = 37
    ConjointInReverse = 38
    ConjointOut = 39
    ConjointOutReverse = 40
    ConjointAtop = 41
    ConjointAtopReverse = 42
    ConjointXor = 43
    Multiply = 48
    Screen = 49
    Overlay = 50
    Darken = 51
    Lighten = 52
    ColorDodge = 53
    ColorBurn = 54
    HardLight = 55
    SoftLight = 56
    Difference = 57
    Exclusion = 58
    HSLHue = 59
    HSLSaturation = 60
    HSLColor = 61
    HSLLuminosity = 62
class PolyEdge:
    Sharp = 0
    Smooth = 1
class PolyMode:
    Precise = 0
    Imprecise = 1
class CP:
    Repeat = 1 << 0
    AlphaMap = 1 << 1
    AlphaXOrigin = 1 << 2
    AlphaYOrigin = 1 << 3
    ClipXOrigin = 1 << 4
    ClipYOrigin = 1 << 5
    ClipMask = 1 << 6
    GraphicsExposure = 1 << 7
    SubwindowMode = 1 << 8
    PolyEdge = 1 << 9
    PolyMode = 1 << 10
    Dither = 1 << 11
    ComponentAlpha = 1 << 12
class SubPixel:
    Unknown = 0
    HorizontalRGB = 1
    HorizontalBGR = 2
    VerticalRGB = 3
    VerticalBGR = 4
    _None = 5
class Repeat:
    _None = 0
    Normal = 1
    Pad = 2
    Reflect = 3
class DIRECTFORMAT(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.red_shift, self.red_mask, self.green_shift, self.green_mask, self.blue_shift, self.blue_mask, self.alpha_shift, self.alpha_mask = unpacker.unpack("HHHHHHHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHHHHHH", self.red_shift, self.red_mask, self.green_shift, self.green_mask, self.blue_shift, self.blue_mask, self.alpha_shift, self.alpha_mask))
        return buf.getvalue()
    fixed_size = 16
class PICTFORMINFO(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.id, self.type, self.depth = unpacker.unpack("IBB2x")
        self.direct = DIRECTFORMAT(unpacker)
        self.colormap, = unpacker.unpack("I")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IBB2xI", self.id, self.type, self.depth, self.colormap))
        buf.write(self.direct.pack())
        return buf.getvalue()
class PICTVISUAL(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.visual, self.format = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.visual, self.format))
        return buf.getvalue()
    fixed_size = 8
class PICTDEPTH(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.depth, self.num_visuals = unpacker.unpack("BxH4x")
        self.visuals = xcffib.List(unpacker, PICTVISUAL, self.num_visuals)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BxH4x", self.depth, self.num_visuals))
        buf.write(xcffib.pack_list(self.visuals, PICTVISUAL))
        return buf.getvalue()
class PICTSCREEN(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.num_depths, self.fallback = unpacker.unpack("II")
        self.depths = xcffib.List(unpacker, PICTDEPTH, self.num_depths)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.num_depths, self.fallback))
        buf.write(xcffib.pack_list(self.depths, PICTDEPTH))
        return buf.getvalue()
class INDEXVALUE(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.pixel, self.red, self.green, self.blue, self.alpha = unpacker.unpack("IHHHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IHHHH", self.pixel, self.red, self.green, self.blue, self.alpha))
        return buf.getvalue()
    fixed_size = 12
class COLOR(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.red, self.green, self.blue, self.alpha = unpacker.unpack("HHHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHH", self.red, self.green, self.blue, self.alpha))
        return buf.getvalue()
    fixed_size = 8
class POINTFIX(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.x, self.y = unpacker.unpack("ii")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=ii", self.x, self.y))
        return buf.getvalue()
    fixed_size = 8
class LINEFIX(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.p1 = POINTFIX(unpacker)
        unpacker.pad(POINTFIX)
        self.p2 = POINTFIX(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(self.p1.pack())
        buf.write(self.p2.pack())
        return buf.getvalue()
class TRIANGLE(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.p1 = POINTFIX(unpacker)
        unpacker.pad(POINTFIX)
        self.p2 = POINTFIX(unpacker)
        unpacker.pad(POINTFIX)
        self.p3 = POINTFIX(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(self.p1.pack())
        buf.write(self.p2.pack())
        buf.write(self.p3.pack())
        return buf.getvalue()
class TRAPEZOID(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.top, self.bottom = unpacker.unpack("ii")
        self.left = LINEFIX(unpacker)
        unpacker.pad(LINEFIX)
        self.right = LINEFIX(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=ii", self.top, self.bottom))
        buf.write(self.left.pack())
        buf.write(self.right.pack())
        return buf.getvalue()
class GLYPHINFO(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.width, self.height, self.x, self.y, self.x_off, self.y_off = unpacker.unpack("HHhhhh")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHhhhh", self.width, self.height, self.x, self.y, self.x_off, self.y_off))
        return buf.getvalue()
    fixed_size = 12
class QueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xII16x")
        self.bufsize = unpacker.offset - base
class QueryVersionCookie(xcffib.Cookie):
    reply_type = QueryVersionReply
class QueryPictFormatsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_formats, self.num_screens, self.num_depths, self.num_visuals, self.num_subpixel = unpacker.unpack("xx2x4xIIIII4x")
        self.formats = xcffib.List(unpacker, PICTFORMINFO, self.num_formats)
        unpacker.pad(PICTSCREEN)
        self.screens = xcffib.List(unpacker, PICTSCREEN, self.num_screens)
        unpacker.pad("I")
        self.subpixels = xcffib.List(unpacker, "I", self.num_subpixel)
        self.bufsize = unpacker.offset - base
class QueryPictFormatsCookie(xcffib.Cookie):
    reply_type = QueryPictFormatsReply
class QueryPictIndexValuesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_values, = unpacker.unpack("xx2x4xI20x")
        self.values = xcffib.List(unpacker, INDEXVALUE, self.num_values)
        self.bufsize = unpacker.offset - base
class QueryPictIndexValuesCookie(xcffib.Cookie):
    reply_type = QueryPictIndexValuesReply
class TRANSFORM(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.matrix11, self.matrix12, self.matrix13, self.matrix21, self.matrix22, self.matrix23, self.matrix31, self.matrix32, self.matrix33 = unpacker.unpack("iiiiiiiii")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=iiiiiiiii", self.matrix11, self.matrix12, self.matrix13, self.matrix21, self.matrix22, self.matrix23, self.matrix31, self.matrix32, self.matrix33))
        return buf.getvalue()
    fixed_size = 36
class QueryFiltersReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_aliases, self.num_filters = unpacker.unpack("xx2x4xII16x")
        self.aliases = xcffib.List(unpacker, "H", self.num_aliases)
        unpacker.pad(xproto.STR)
        self.filters = xcffib.List(unpacker, xproto.STR, self.num_filters)
        self.bufsize = unpacker.offset - base
class QueryFiltersCookie(xcffib.Cookie):
    reply_type = QueryFiltersReply
class ANIMCURSORELT(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.cursor, self.delay = unpacker.unpack("II")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=II", self.cursor, self.delay))
        return buf.getvalue()
    fixed_size = 8
class SPANFIX(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.l, self.r, self.y = unpacker.unpack("iii")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=iii", self.l, self.r, self.y))
        return buf.getvalue()
    fixed_size = 12
class TRAP(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.top = SPANFIX(unpacker)
        unpacker.pad(SPANFIX)
        self.bot = SPANFIX(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(self.top.pack())
        buf.write(self.bot.pack())
        return buf.getvalue()
class renderExtension(xcffib.Extension):
    def QueryVersion(self, client_major_version, client_minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", client_major_version, client_minor_version))
        return self.send_request(0, buf, QueryVersionCookie, is_checked=is_checked)
    def QueryPictFormats(self, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        return self.send_request(1, buf, QueryPictFormatsCookie, is_checked=is_checked)
    def QueryPictIndexValues(self, format, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", format))
        return self.send_request(2, buf, QueryPictIndexValuesCookie, is_checked=is_checked)
    def CreatePicture(self, pid, drawable, format, value_mask, value_list, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIII", pid, drawable, format))
        buf.write(struct.pack("=I", value_mask))
        buf.write(xcffib.pack_list(value_list, "I"))
        return self.send_request(4, buf, is_checked=is_checked)
    def ChangePicture(self, picture, value_mask, value_list, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", picture))
        buf.write(struct.pack("=I", value_mask))
        buf.write(xcffib.pack_list(value_list, "I"))
        return self.send_request(5, buf, is_checked=is_checked)
    def SetPictureClipRectangles(self, picture, clip_x_origin, clip_y_origin, rectangles, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIhh", picture, clip_x_origin, clip_y_origin))
        buf.write(xcffib.pack_list(rectangles, xproto.RECTANGLE))
        return self.send_request(6, buf, is_checked=is_checked)
    def FreePicture(self, picture, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", picture))
        return self.send_request(7, buf, is_checked=is_checked)
    def Composite(self, op, src, mask, dst, src_x, src_y, mask_x, mask_y, dst_x, dst_y, width, height, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIhhhhhhHH", op, src, mask, dst, src_x, src_y, mask_x, mask_y, dst_x, dst_y, width, height))
        return self.send_request(8, buf, is_checked=is_checked)
    def Trapezoids(self, op, src, dst, mask_format, src_x, src_y, traps, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIhh", op, src, dst, mask_format, src_x, src_y))
        buf.write(xcffib.pack_list(traps, TRAPEZOID))
        return self.send_request(10, buf, is_checked=is_checked)
    def Triangles(self, op, src, dst, mask_format, src_x, src_y, triangles, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIhh", op, src, dst, mask_format, src_x, src_y))
        buf.write(xcffib.pack_list(triangles, TRIANGLE))
        return self.send_request(11, buf, is_checked=is_checked)
    def TriStrip(self, op, src, dst, mask_format, src_x, src_y, points, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIhh", op, src, dst, mask_format, src_x, src_y))
        buf.write(xcffib.pack_list(points, POINTFIX))
        return self.send_request(12, buf, is_checked=is_checked)
    def TriFan(self, op, src, dst, mask_format, src_x, src_y, points, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIhh", op, src, dst, mask_format, src_x, src_y))
        buf.write(xcffib.pack_list(points, POINTFIX))
        return self.send_request(13, buf, is_checked=is_checked)
    def CreateGlyphSet(self, gsid, format, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", gsid, format))
        return self.send_request(17, buf, is_checked=is_checked)
    def ReferenceGlyphSet(self, gsid, existing, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", gsid, existing))
        return self.send_request(18, buf, is_checked=is_checked)
    def FreeGlyphSet(self, glyphset, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", glyphset))
        return self.send_request(19, buf, is_checked=is_checked)
    def AddGlyphs(self, glyphset, glyphs_len, glyphids, glyphs, data, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", glyphset, glyphs_len))
        buf.write(xcffib.pack_list(glyphids, "I"))
        buf.write(xcffib.pack_list(glyphs, GLYPHINFO))
        buf.write(xcffib.pack_list(data, "B"))
        return self.send_request(20, buf, is_checked=is_checked)
    def FreeGlyphs(self, glyphset, glyphs, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", glyphset))
        buf.write(xcffib.pack_list(glyphs, "I"))
        return self.send_request(22, buf, is_checked=is_checked)
    def CompositeGlyphs8(self, op, src, dst, mask_format, glyphset, src_x, src_y, glyphcmds, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIIhh", op, src, dst, mask_format, glyphset, src_x, src_y))
        buf.write(xcffib.pack_list(glyphcmds, "B"))
        return self.send_request(23, buf, is_checked=is_checked)
    def CompositeGlyphs16(self, op, src, dst, mask_format, glyphset, src_x, src_y, glyphcmds, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIIhh", op, src, dst, mask_format, glyphset, src_x, src_y))
        buf.write(xcffib.pack_list(glyphcmds, "B"))
        return self.send_request(24, buf, is_checked=is_checked)
    def CompositeGlyphs32(self, op, src, dst, mask_format, glyphset, src_x, src_y, glyphcmds, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xIIIIhh", op, src, dst, mask_format, glyphset, src_x, src_y))
        buf.write(xcffib.pack_list(glyphcmds, "B"))
        return self.send_request(25, buf, is_checked=is_checked)
    def FillRectangles(self, op, dst, color, rects, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3xI", op, dst))
        buf.write(color.pack())
        buf.write(xcffib.pack_list(rects, xproto.RECTANGLE))
        return self.send_request(26, buf, is_checked=is_checked)
    def CreateCursor(self, cid, source, x, y, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIHH", cid, source, x, y))
        return self.send_request(27, buf, is_checked=is_checked)
    def SetPictureTransform(self, picture, transform, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", picture))
        buf.write(transform.pack())
        return self.send_request(28, buf, is_checked=is_checked)
    def QueryFilters(self, drawable, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", drawable))
        return self.send_request(29, buf, QueryFiltersCookie, is_checked=is_checked)
    def SetPictureFilter(self, picture, filter_len, filter, values, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", picture, filter_len))
        buf.write(xcffib.pack_list(filter, "c"))
        buf.write(xcffib.pack_list(values, "i"))
        return self.send_request(30, buf, is_checked=is_checked)
    def CreateAnimCursor(self, cid, cursors, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", cid))
        buf.write(xcffib.pack_list(cursors, ANIMCURSORELT))
        return self.send_request(31, buf, is_checked=is_checked)
    def AddTraps(self, picture, x_off, y_off, traps, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIhh", picture, x_off, y_off))
        buf.write(xcffib.pack_list(traps, TRAP))
        return self.send_request(32, buf, is_checked=is_checked)
    def CreateSolidFill(self, picture, color, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", picture))
        buf.write(color.pack())
        return self.send_request(33, buf, is_checked=is_checked)
    def CreateLinearGradient(self, picture, num_stops, p1, p2, stops, colors, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xII", picture, num_stops))
        buf.write(p1.pack())
        buf.write(p2.pack())
        buf.write(xcffib.pack_list(stops, "i"))
        buf.write(xcffib.pack_list(colors, COLOR))
        return self.send_request(34, buf, is_checked=is_checked)
    def CreateRadialGradient(self, picture, inner_radius, outer_radius, num_stops, inner, outer, stops, colors, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIiiI", picture, inner_radius, outer_radius, num_stops))
        buf.write(inner.pack())
        buf.write(outer.pack())
        buf.write(xcffib.pack_list(stops, "i"))
        buf.write(xcffib.pack_list(colors, COLOR))
        return self.send_request(35, buf, is_checked=is_checked)
    def CreateConicalGradient(self, picture, angle, num_stops, center, stops, colors, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIiI", picture, angle, num_stops))
        buf.write(center.pack())
        buf.write(xcffib.pack_list(stops, "i"))
        buf.write(xcffib.pack_list(colors, COLOR))
        return self.send_request(36, buf, is_checked=is_checked)
xcffib._add_ext(key, renderExtension, _events, _errors)

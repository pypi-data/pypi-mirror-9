import xcffib
import struct
import six
MAJOR_VERSION = 2
MINOR_VERSION = 3
key = xcffib.ExtensionKey("XInputExtension")
_events = {}
_errors = {}
from . import xfixes
from . import xproto
class FP3232(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.integral, self.frac = unpacker.unpack("iI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=iI", self.integral, self.frac))
        return buf.getvalue()
    fixed_size = 8
class GetExtensionVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.server_major, self.server_minor, self.present = unpacker.unpack("xx2x4xHHB19x")
        self.bufsize = unpacker.offset - base
class GetExtensionVersionCookie(xcffib.Cookie):
    reply_type = GetExtensionVersionReply
class DeviceUse:
    IsXPointer = 0
    IsXKeyboard = 1
    IsXExtensionDevice = 2
    IsXExtensionKeyboard = 3
    IsXExtensionPointer = 4
class InputClass:
    Key = 0
    Button = 1
    Valuator = 2
    Feedback = 3
    Proximity = 4
    Focus = 5
    Other = 6
class ValuatorMode:
    Relative = 0
    Absolute = 1
class DeviceInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.device_type, self.device_id, self.num_class_info, self.device_use = unpacker.unpack("IBBBx")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IBBBx", self.device_type, self.device_id, self.num_class_info, self.device_use))
        return buf.getvalue()
    fixed_size = 8
class KeyInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.min_keycode, self.max_keycode, self.num_keys = unpacker.unpack("BBBBH2x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBBH2x", self.class_id, self.len, self.min_keycode, self.max_keycode, self.num_keys))
        return buf.getvalue()
    fixed_size = 8
class ButtonInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.num_buttons = unpacker.unpack("BBH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH", self.class_id, self.len, self.num_buttons))
        return buf.getvalue()
    fixed_size = 4
class AxisInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.resolution, self.minimum, self.maximum = unpacker.unpack("Iii")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=Iii", self.resolution, self.minimum, self.maximum))
        return buf.getvalue()
    fixed_size = 12
class ValuatorInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.axes_len, self.mode, self.motion_size = unpacker.unpack("BBBBI")
        self.axes = xcffib.List(unpacker, AxisInfo, self.axes_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBBI", self.class_id, self.len, self.axes_len, self.mode, self.motion_size))
        buf.write(xcffib.pack_list(self.axes, AxisInfo))
        return buf.getvalue()
class InputInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len = unpacker.unpack("BB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BB", self.class_id, self.len))
        return buf.getvalue()
    fixed_size = 2
class DeviceName(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.len, = unpacker.unpack("B")
        self.string = xcffib.List(unpacker, "c", self.len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", self.len))
        buf.write(xcffib.pack_list(self.string, "c"))
        return buf.getvalue()
class ListInputDevicesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.devices_len, = unpacker.unpack("xx2x4xB23x")
        self.devices = xcffib.List(unpacker, DeviceInfo, self.devices_len)
        self.bufsize = unpacker.offset - base
class ListInputDevicesCookie(xcffib.Cookie):
    reply_type = ListInputDevicesReply
class InputClassInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.event_type_base = unpacker.unpack("BB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BB", self.class_id, self.event_type_base))
        return buf.getvalue()
    fixed_size = 2
class OpenDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_classes, = unpacker.unpack("xx2x4xB23x")
        self.class_info = xcffib.List(unpacker, InputClassInfo, self.num_classes)
        self.bufsize = unpacker.offset - base
class OpenDeviceCookie(xcffib.Cookie):
    reply_type = OpenDeviceReply
class SetDeviceModeReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class SetDeviceModeCookie(xcffib.Cookie):
    reply_type = SetDeviceModeReply
class GetSelectedExtensionEventsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_this_classes, self.num_all_classes = unpacker.unpack("xx2x4xHH20x")
        self.this_classes = xcffib.List(unpacker, "I", self.num_this_classes)
        unpacker.pad("I")
        self.all_classes = xcffib.List(unpacker, "I", self.num_all_classes)
        self.bufsize = unpacker.offset - base
class GetSelectedExtensionEventsCookie(xcffib.Cookie):
    reply_type = GetSelectedExtensionEventsReply
class PropagateMode:
    AddToList = 0
    DeleteFromList = 1
class GetDeviceDontPropagateListReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_classes, = unpacker.unpack("xx2x4xH22x")
        self.classes = xcffib.List(unpacker, "I", self.num_classes)
        self.bufsize = unpacker.offset - base
class GetDeviceDontPropagateListCookie(xcffib.Cookie):
    reply_type = GetDeviceDontPropagateListReply
class DeviceTimeCoord(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.time, = unpacker.unpack("I")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=I", self.time))
        return buf.getvalue()
    fixed_size = 4
class GetDeviceMotionEventsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_events, self.num_axes, self.device_mode = unpacker.unpack("xx2x4xIBB18x")
        self.bufsize = unpacker.offset - base
class GetDeviceMotionEventsCookie(xcffib.Cookie):
    reply_type = GetDeviceMotionEventsReply
class ChangeKeyboardDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class ChangeKeyboardDeviceCookie(xcffib.Cookie):
    reply_type = ChangeKeyboardDeviceReply
class ChangePointerDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class ChangePointerDeviceCookie(xcffib.Cookie):
    reply_type = ChangePointerDeviceReply
class GrabDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class GrabDeviceCookie(xcffib.Cookie):
    reply_type = GrabDeviceReply
class DeviceInputMode:
    AsyncThisDevice = 0
    SyncThisDevice = 1
    ReplayThisDevice = 2
    AsyncOtherDevices = 3
    AsyncAll = 4
    SyncAll = 5
class GetDeviceFocusReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.focus, self.time, self.revert_to = unpacker.unpack("xx2x4xIIB15x")
        self.bufsize = unpacker.offset - base
class GetDeviceFocusCookie(xcffib.Cookie):
    reply_type = GetDeviceFocusReply
class FeedbackClass:
    Keyboard = 0
    Pointer = 1
    String = 2
    Integer = 3
    Led = 4
    Bell = 5
class KbdFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.pitch, self.duration, self.led_mask, self.led_values, self.global_auto_repeat, self.click, self.percent = unpacker.unpack("BBHHHIIBBBx")
        self.auto_repeats = xcffib.List(unpacker, "B", 32)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHHHIIBBBx", self.class_id, self.feedback_id, self.len, self.pitch, self.duration, self.led_mask, self.led_values, self.global_auto_repeat, self.click, self.percent))
        buf.write(xcffib.pack_list(self.auto_repeats, "B"))
        return buf.getvalue()
    fixed_size = 52
class PtrFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.accel_num, self.accel_denom, self.threshold = unpacker.unpack("BBH2xHHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH2xHHH", self.class_id, self.feedback_id, self.len, self.accel_num, self.accel_denom, self.threshold))
        return buf.getvalue()
    fixed_size = 12
class IntegerFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.resolution, self.min_value, self.max_value = unpacker.unpack("BBHIii")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHIii", self.class_id, self.feedback_id, self.len, self.resolution, self.min_value, self.max_value))
        return buf.getvalue()
    fixed_size = 16
class StringFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.max_symbols, self.num_keysyms = unpacker.unpack("BBHHH")
        self.keysyms = xcffib.List(unpacker, "I", self.num_keysyms)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHHH", self.class_id, self.feedback_id, self.len, self.max_symbols, self.num_keysyms))
        buf.write(xcffib.pack_list(self.keysyms, "I"))
        return buf.getvalue()
class BellFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.percent, self.pitch, self.duration = unpacker.unpack("BBHB3xHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHB3xHH", self.class_id, self.feedback_id, self.len, self.percent, self.pitch, self.duration))
        return buf.getvalue()
    fixed_size = 12
class LedFeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.led_mask, self.led_values = unpacker.unpack("BBHII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHII", self.class_id, self.feedback_id, self.len, self.led_mask, self.led_values))
        return buf.getvalue()
    fixed_size = 12
class FeedbackState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len = unpacker.unpack("BBH")
        self.uninterpreted_data = xcffib.List(unpacker, "B", self.len - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH", self.class_id, self.feedback_id, self.len))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class GetFeedbackControlReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_feedbacks, = unpacker.unpack("xx2x4xH22x")
        self.feedbacks = xcffib.List(unpacker, FeedbackState, self.num_feedbacks)
        self.bufsize = unpacker.offset - base
class GetFeedbackControlCookie(xcffib.Cookie):
    reply_type = GetFeedbackControlReply
class KbdFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.key, self.auto_repeat_mode, self.key_click_percent, self.bell_percent, self.bell_pitch, self.bell_duration, self.led_mask, self.led_values = unpacker.unpack("BBHBBbbhhII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHBBbbhhII", self.class_id, self.feedback_id, self.len, self.key, self.auto_repeat_mode, self.key_click_percent, self.bell_percent, self.bell_pitch, self.bell_duration, self.led_mask, self.led_values))
        return buf.getvalue()
    fixed_size = 20
class PtrFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.num, self.denom, self.threshold = unpacker.unpack("BBH2xhhh")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH2xhhh", self.class_id, self.feedback_id, self.len, self.num, self.denom, self.threshold))
        return buf.getvalue()
    fixed_size = 12
class IntegerFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.int_to_display = unpacker.unpack("BBHi")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHi", self.class_id, self.feedback_id, self.len, self.int_to_display))
        return buf.getvalue()
    fixed_size = 8
class StringFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.num_keysyms = unpacker.unpack("BBH2xH")
        self.keysyms = xcffib.List(unpacker, "I", self.num_keysyms)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH2xH", self.class_id, self.feedback_id, self.len, self.num_keysyms))
        buf.write(xcffib.pack_list(self.keysyms, "I"))
        return buf.getvalue()
class BellFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.percent, self.pitch, self.duration = unpacker.unpack("BBHb3xhh")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHb3xhh", self.class_id, self.feedback_id, self.len, self.percent, self.pitch, self.duration))
        return buf.getvalue()
    fixed_size = 12
class LedFeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len, self.led_mask, self.led_values = unpacker.unpack("BBHII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBHII", self.class_id, self.feedback_id, self.len, self.led_mask, self.led_values))
        return buf.getvalue()
    fixed_size = 12
class FeedbackCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.feedback_id, self.len = unpacker.unpack("BBH")
        self.uninterpreted_data = xcffib.List(unpacker, "B", self.len - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBH", self.class_id, self.feedback_id, self.len))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class GetDeviceKeyMappingReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.keysyms_per_keycode, = unpacker.unpack("xx2x4xB23x")
        self.keysyms = xcffib.List(unpacker, "I", self.length)
        self.bufsize = unpacker.offset - base
class GetDeviceKeyMappingCookie(xcffib.Cookie):
    reply_type = GetDeviceKeyMappingReply
class GetDeviceModifierMappingReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.keycodes_per_modifier, = unpacker.unpack("xx2x4xB23x")
        self.keymaps = xcffib.List(unpacker, "B", self.keycodes_per_modifier * 8)
        self.bufsize = unpacker.offset - base
class GetDeviceModifierMappingCookie(xcffib.Cookie):
    reply_type = GetDeviceModifierMappingReply
class SetDeviceModifierMappingReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class SetDeviceModifierMappingCookie(xcffib.Cookie):
    reply_type = SetDeviceModifierMappingReply
class GetDeviceButtonMappingReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.map_size, = unpacker.unpack("xx2x4xB23x")
        self.map = xcffib.List(unpacker, "B", self.map_size)
        self.bufsize = unpacker.offset - base
class GetDeviceButtonMappingCookie(xcffib.Cookie):
    reply_type = GetDeviceButtonMappingReply
class SetDeviceButtonMappingReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class SetDeviceButtonMappingCookie(xcffib.Cookie):
    reply_type = SetDeviceButtonMappingReply
class KeyState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.num_keys = unpacker.unpack("BBBx")
        self.keys = xcffib.List(unpacker, "B", 32)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBx", self.class_id, self.len, self.num_keys))
        buf.write(xcffib.pack_list(self.keys, "B"))
        return buf.getvalue()
    fixed_size = 36
class ButtonState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.num_buttons = unpacker.unpack("BBBx")
        self.buttons = xcffib.List(unpacker, "B", 32)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBx", self.class_id, self.len, self.num_buttons))
        buf.write(xcffib.pack_list(self.buttons, "B"))
        return buf.getvalue()
    fixed_size = 36
class ValuatorState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.num_valuators, self.mode = unpacker.unpack("BBBB")
        self.valuators = xcffib.List(unpacker, "I", self.num_valuators)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBB", self.class_id, self.len, self.num_valuators, self.mode))
        buf.write(xcffib.pack_list(self.valuators, "I"))
        return buf.getvalue()
class InputState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.class_id, self.len, self.num_items = unpacker.unpack("BBBx")
        self.uninterpreted_data = xcffib.List(unpacker, "B", self.len - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBx", self.class_id, self.len, self.num_items))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class QueryDeviceStateReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_classes, = unpacker.unpack("xx2x4xB23x")
        self.classes = xcffib.List(unpacker, InputState, self.num_classes)
        self.bufsize = unpacker.offset - base
class QueryDeviceStateCookie(xcffib.Cookie):
    reply_type = QueryDeviceStateReply
class SetDeviceValuatorsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class SetDeviceValuatorsCookie(xcffib.Cookie):
    reply_type = SetDeviceValuatorsReply
class DeviceControl:
    resolution = 1
    abs_calib = 2
    core = 3
    enable = 4
    abs_area = 5
class DeviceResolutionState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.num_valuators = unpacker.unpack("HHI")
        self.resolution_values = xcffib.List(unpacker, "I", self.num_valuators)
        unpacker.pad("I")
        self.resolution_min = xcffib.List(unpacker, "I", self.num_valuators)
        unpacker.pad("I")
        self.resolution_max = xcffib.List(unpacker, "I", self.num_valuators)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHI", self.control_id, self.len, self.num_valuators))
        buf.write(xcffib.pack_list(self.resolution_values, "I"))
        buf.write(xcffib.pack_list(self.resolution_min, "I"))
        buf.write(xcffib.pack_list(self.resolution_max, "I"))
        return buf.getvalue()
class DeviceAbsCalibState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.min_x, self.max_x, self.min_y, self.max_y, self.flip_x, self.flip_y, self.rotation, self.button_threshold = unpacker.unpack("HHiiiiIIII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHiiiiIIII", self.control_id, self.len, self.min_x, self.max_x, self.min_y, self.max_y, self.flip_x, self.flip_y, self.rotation, self.button_threshold))
        return buf.getvalue()
    fixed_size = 36
class DeviceAbsAreaState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.offset_x, self.offset_y, self.width, self.height, self.screen, self.following = unpacker.unpack("HHIIIIII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHIIIIII", self.control_id, self.len, self.offset_x, self.offset_y, self.width, self.height, self.screen, self.following))
        return buf.getvalue()
    fixed_size = 28
class DeviceCoreState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.status, self.iscore = unpacker.unpack("HHBB2x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHBB2x", self.control_id, self.len, self.status, self.iscore))
        return buf.getvalue()
    fixed_size = 8
class DeviceEnableState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.enable = unpacker.unpack("HHB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHB3x", self.control_id, self.len, self.enable))
        return buf.getvalue()
    fixed_size = 8
class DeviceState(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len = unpacker.unpack("HH")
        self.uninterpreted_data = xcffib.List(unpacker, "B", self.len - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HH", self.control_id, self.len))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class GetDeviceControlReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.control = DeviceState(unpacker)
        self.bufsize = unpacker.offset - base
class GetDeviceControlCookie(xcffib.Cookie):
    reply_type = GetDeviceControlReply
class DeviceResolutionCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.first_valuator, self.num_valuators = unpacker.unpack("HHBB")
        self.resolution_values = xcffib.List(unpacker, "I", self.num_valuators)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHBB", self.control_id, self.len, self.first_valuator, self.num_valuators))
        buf.write(xcffib.pack_list(self.resolution_values, "I"))
        return buf.getvalue()
class DeviceAbsCalibCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.min_x, self.max_x, self.min_y, self.max_y, self.flip_x, self.flip_y, self.rotation, self.button_threshold = unpacker.unpack("HHiiiiIIII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHiiiiIIII", self.control_id, self.len, self.min_x, self.max_x, self.min_y, self.max_y, self.flip_x, self.flip_y, self.rotation, self.button_threshold))
        return buf.getvalue()
    fixed_size = 36
class DeviceAbsAreaCtrl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.offset_x, self.offset_y, self.width, self.height, self.screen, self.following = unpacker.unpack("HHIIiiiI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHIIiiiI", self.control_id, self.len, self.offset_x, self.offset_y, self.width, self.height, self.screen, self.following))
        return buf.getvalue()
    fixed_size = 28
class DeviceCoreCtrl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.status = unpacker.unpack("HHB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHB3x", self.control_id, self.len, self.status))
        return buf.getvalue()
    fixed_size = 8
class DeviceEnableCtrl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len, self.enable = unpacker.unpack("HHB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHB3x", self.control_id, self.len, self.enable))
        return buf.getvalue()
    fixed_size = 8
class DeviceCtl(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.control_id, self.len = unpacker.unpack("HH")
        self.uninterpreted_data = xcffib.List(unpacker, "B", self.len - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HH", self.control_id, self.len))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class ChangeDeviceControlReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class ChangeDeviceControlCookie(xcffib.Cookie):
    reply_type = ChangeDeviceControlReply
class ListDevicePropertiesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_atoms, = unpacker.unpack("xx2x4xH22x")
        self.atoms = xcffib.List(unpacker, "I", self.num_atoms)
        self.bufsize = unpacker.offset - base
class ListDevicePropertiesCookie(xcffib.Cookie):
    reply_type = ListDevicePropertiesReply
class PropertyFormat:
    _8Bits = 8
    _16Bits = 16
    _32Bits = 32
class GetDevicePropertyReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.bytes_after, self.num_items, self.format, self.device_id = unpacker.unpack("xx2x4xIIIBB10x")
        self.bufsize = unpacker.offset - base
class GetDevicePropertyCookie(xcffib.Cookie):
    reply_type = GetDevicePropertyReply
class Device:
    All = 0
    AllMaster = 1
class GroupInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.base, self.latched, self.locked, self.effective = unpacker.unpack("BBBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=BBBB", self.base, self.latched, self.locked, self.effective))
        return buf.getvalue()
    fixed_size = 4
class ModifierInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.base, self.latched, self.locked, self.effective = unpacker.unpack("IIII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IIII", self.base, self.latched, self.locked, self.effective))
        return buf.getvalue()
    fixed_size = 16
class XIQueryPointerReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.root, self.child, self.root_x, self.root_y, self.win_x, self.win_y, self.same_screen, self.buttons_len = unpacker.unpack("xx2x4xIIiiiiBxH")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.buttons = xcffib.List(unpacker, "I", self.buttons_len)
        self.bufsize = unpacker.offset - base
class XIQueryPointerCookie(xcffib.Cookie):
    reply_type = XIQueryPointerReply
class HierarchyChangeType:
    AddMaster = 1
    RemoveMaster = 2
    AttachSlave = 3
    DetachSlave = 4
class ChangeMode:
    Attach = 1
    Float = 2
class AddMaster(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.name_len, self.send_core, self.enable = unpacker.unpack("HHHBB")
        self.name = xcffib.List(unpacker, "c", self.name_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHBB", self.type, self.len, self.name_len, self.send_core, self.enable))
        buf.write(xcffib.pack_list(self.name, "c"))
        return buf.getvalue()
class RemoveMaster(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.deviceid, self.return_mode, self.return_pointer, self.return_keyboard = unpacker.unpack("HHHBxHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHBxHH", self.type, self.len, self.deviceid, self.return_mode, self.return_pointer, self.return_keyboard))
        return buf.getvalue()
    fixed_size = 12
class AttachSlave(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.deviceid, self.master = unpacker.unpack("HHHH")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHH", self.type, self.len, self.deviceid, self.master))
        return buf.getvalue()
    fixed_size = 8
class DetachSlave(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.deviceid = unpacker.unpack("HHH2x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHH2x", self.type, self.len, self.deviceid))
        return buf.getvalue()
    fixed_size = 8
class HierarchyChange(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len = unpacker.unpack("HH")
        self.uninterpreted_data = xcffib.List(unpacker, "B", (self.len * 4) - 4)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HH", self.type, self.len))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class XIGetClientPointerReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.set, self.deviceid = unpacker.unpack("xx2x4xBxH20x")
        self.bufsize = unpacker.offset - base
class XIGetClientPointerCookie(xcffib.Cookie):
    reply_type = XIGetClientPointerReply
class XIEventMask:
    DeviceChanged = 1 << 1
    KeyPress = 1 << 2
    KeyRelease = 1 << 3
    ButtonPress = 1 << 4
    ButtonRelease = 1 << 5
    Motion = 1 << 6
    Enter = 1 << 7
    Leave = 1 << 8
    FocusIn = 1 << 9
    FocusOut = 1 << 10
    Hierarchy = 1 << 11
    Property = 1 << 12
    RawKeyPress = 1 << 13
    RawKeyRelease = 1 << 14
    RawButtonPress = 1 << 15
    RawButtonRelease = 1 << 16
    RawMotion = 1 << 17
    TouchBegin = 1 << 18
    TouchUpdate = 1 << 19
    TouchEnd = 1 << 20
    TouchOwnership = 1 << 21
    RawTouchBegin = 1 << 22
    RawTouchUpdate = 1 << 23
    RawTouchEnd = 1 << 24
    BarrierHit = 1 << 25
    BarrierLeave = 1 << 26
class EventMask(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.mask_len = unpacker.unpack("HH")
        self.mask = xcffib.List(unpacker, "I", self.mask_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HH", self.deviceid, self.mask_len))
        buf.write(xcffib.pack_list(self.mask, "I"))
        return buf.getvalue()
class XIQueryVersionReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.major_version, self.minor_version = unpacker.unpack("xx2x4xHH20x")
        self.bufsize = unpacker.offset - base
class XIQueryVersionCookie(xcffib.Cookie):
    reply_type = XIQueryVersionReply
class DeviceClassType:
    Key = 0
    Button = 1
    Valuator = 2
    Scroll = 3
    Touch = 8
class DeviceType:
    MasterPointer = 1
    MasterKeyboard = 2
    SlavePointer = 3
    SlaveKeyboard = 4
    FloatingSlave = 5
class ScrollFlags:
    NoEmulation = 1 << 0
    Preferred = 1 << 1
class ScrollType:
    Vertical = 1
    Horizontal = 2
class TouchMode:
    Direct = 1
    Dependent = 2
class ButtonClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid, self.num_buttons = unpacker.unpack("HHHH")
        self.state = xcffib.List(unpacker, "I", (self.num_buttons + 31) // 32)
        unpacker.pad("I")
        self.labels = xcffib.List(unpacker, "I", self.num_buttons)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHH", self.type, self.len, self.sourceid, self.num_buttons))
        buf.write(xcffib.pack_list(self.state, "I"))
        buf.write(xcffib.pack_list(self.labels, "I"))
        return buf.getvalue()
class KeyClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid, self.num_keys = unpacker.unpack("HHHH")
        self.keys = xcffib.List(unpacker, "I", self.num_keys)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHH", self.type, self.len, self.sourceid, self.num_keys))
        buf.write(xcffib.pack_list(self.keys, "I"))
        return buf.getvalue()
class ScrollClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid, self.number, self.scroll_type, self.flags = unpacker.unpack("HHHHH2xI")
        self.increment = FP3232(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHHH2xI", self.type, self.len, self.sourceid, self.number, self.scroll_type, self.flags))
        buf.write(self.increment.pack())
        return buf.getvalue()
class TouchClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid, self.mode, self.num_touches = unpacker.unpack("HHHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHBB", self.type, self.len, self.sourceid, self.mode, self.num_touches))
        return buf.getvalue()
    fixed_size = 8
class ValuatorClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid, self.number, self.label = unpacker.unpack("HHHHI")
        self.min = FP3232(unpacker)
        unpacker.pad(FP3232)
        self.max = FP3232(unpacker)
        unpacker.pad(FP3232)
        self.value = FP3232(unpacker)
        self.resolution, self.mode = unpacker.unpack("IB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHHIIB3x", self.type, self.len, self.sourceid, self.number, self.label, self.resolution, self.mode))
        buf.write(self.min.pack())
        buf.write(self.max.pack())
        buf.write(self.value.pack())
        return buf.getvalue()
class DeviceClass(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.len, self.sourceid = unpacker.unpack("HHH2x")
        self.uninterpreted_data = xcffib.List(unpacker, "B", (self.len * 4) - 8)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHH2x", self.type, self.len, self.sourceid))
        buf.write(xcffib.pack_list(self.uninterpreted_data, "B"))
        return buf.getvalue()
class XIDeviceInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.type, self.attachment, self.num_classes, self.name_len, self.enabled = unpacker.unpack("HHHHHBx")
        self.name = xcffib.List(unpacker, "c", ((self.name_len + 3) // 4) * 4)
        unpacker.pad(DeviceClass)
        self.classes = xcffib.List(unpacker, DeviceClass, self.num_classes)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHHHHBx", self.deviceid, self.type, self.attachment, self.num_classes, self.name_len, self.enabled))
        buf.write(xcffib.pack_list(self.name, "c"))
        buf.write(xcffib.pack_list(self.classes, DeviceClass))
        return buf.getvalue()
class XIQueryDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_infos, = unpacker.unpack("xx2x4xH22x")
        self.infos = xcffib.List(unpacker, XIDeviceInfo, self.num_infos)
        self.bufsize = unpacker.offset - base
class XIQueryDeviceCookie(xcffib.Cookie):
    reply_type = XIQueryDeviceReply
class XIGetFocusReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.focus, = unpacker.unpack("xx2x4xI20x")
        self.bufsize = unpacker.offset - base
class XIGetFocusCookie(xcffib.Cookie):
    reply_type = XIGetFocusReply
class GrabOwner:
    NoOwner = 0
    Owner = 1
class XIGrabDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.status, = unpacker.unpack("xx2x4xB23x")
        self.bufsize = unpacker.offset - base
class XIGrabDeviceCookie(xcffib.Cookie):
    reply_type = XIGrabDeviceReply
class EventMode:
    AsyncDevice = 0
    SyncDevice = 1
    ReplayDevice = 2
    AsyncPairedDevice = 3
    AsyncPair = 4
    SyncPair = 5
    AcceptTouch = 6
    RejectTouch = 7
class GrabMode22:
    Sync = 0
    Async = 1
    Touch = 2
class GrabType:
    Button = 0
    Keycode = 1
    Enter = 2
    FocusIn = 3
    TouchBegin = 4
class ModifierMask:
    Any = 1 << 31
class GrabModifierInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.modifiers, self.status = unpacker.unpack("IB3x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=IB3x", self.modifiers, self.status))
        return buf.getvalue()
    fixed_size = 8
class XIPassiveGrabDeviceReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_modifiers, = unpacker.unpack("xx2x4xH22x")
        self.modifiers = xcffib.List(unpacker, GrabModifierInfo, self.num_modifiers)
        self.bufsize = unpacker.offset - base
class XIPassiveGrabDeviceCookie(xcffib.Cookie):
    reply_type = XIPassiveGrabDeviceReply
class XIListPropertiesReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_properties, = unpacker.unpack("xx2x4xH22x")
        self.properties = xcffib.List(unpacker, "I", self.num_properties)
        self.bufsize = unpacker.offset - base
class XIListPropertiesCookie(xcffib.Cookie):
    reply_type = XIListPropertiesReply
class XIGetPropertyReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.type, self.bytes_after, self.num_items, self.format = unpacker.unpack("xx2x4xIIIB11x")
        self.bufsize = unpacker.offset - base
class XIGetPropertyCookie(xcffib.Cookie):
    reply_type = XIGetPropertyReply
class XIGetSelectedEventsReply(xcffib.Reply):
    def __init__(self, unpacker):
        xcffib.Reply.__init__(self, unpacker)
        base = unpacker.offset
        self.num_masks, = unpacker.unpack("xx2x4xH22x")
        self.masks = xcffib.List(unpacker, EventMask, self.num_masks)
        self.bufsize = unpacker.offset - base
class XIGetSelectedEventsCookie(xcffib.Cookie):
    reply_type = XIGetSelectedEventsReply
class BarrierReleasePointerInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.barrier, self.eventid = unpacker.unpack("H2xII")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=H2xII", self.deviceid, self.barrier, self.eventid))
        return buf.getvalue()
    fixed_size = 12
class DeviceValuatorEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, self.device_state, self.num_valuators, self.first_valuator = unpacker.unpack("xB2xHBB")
        self.valuators = xcffib.List(unpacker, "i", 6)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 0))
        buf.write(struct.pack("=B2xHBB", self.device_id, self.device_state, self.num_valuators, self.first_valuator))
        buf.write(xcffib.pack_list(self.valuators, "i"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[0] = DeviceValuatorEvent
class DeviceKeyPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 1))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[1] = DeviceKeyPressEvent
class DeviceKeyReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 2))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[2] = DeviceKeyReleaseEvent
class DeviceButtonPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 3))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[3] = DeviceButtonPressEvent
class DeviceButtonReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 4))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[4] = DeviceButtonReleaseEvent
class DeviceMotionNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 5))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[5] = DeviceMotionNotifyEvent
class DeviceFocusInEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.window, self.mode, self.device_id = unpacker.unpack("xB2xIIBB18x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 6))
        buf.write(struct.pack("=B2xIIBB18x", self.detail, self.time, self.window, self.mode, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[6] = DeviceFocusInEvent
class DeviceFocusOutEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.window, self.mode, self.device_id = unpacker.unpack("xB2xIIBB18x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 7))
        buf.write(struct.pack("=B2xIIBB18x", self.detail, self.time, self.window, self.mode, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[7] = DeviceFocusOutEvent
class ProximityInEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 8))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[8] = ProximityInEvent
class ProximityOutEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id = unpacker.unpack("xB2xIIIIhhhhHBB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 9))
        buf.write(struct.pack("=B2xIIIIhhhhHBB", self.detail, self.time, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.state, self.same_screen, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[9] = ProximityOutEvent
class DeviceStateNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, self.time, self.num_keys, self.num_buttons, self.num_valuators, self.classes_reported = unpacker.unpack("xB2xIBBBB")
        self.buttons = xcffib.List(unpacker, "B", 4)
        unpacker.pad("B")
        self.keys = xcffib.List(unpacker, "B", 4)
        unpacker.pad("I")
        self.valuators = xcffib.List(unpacker, "I", 3)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 10))
        buf.write(struct.pack("=B2xIBBBB", self.device_id, self.time, self.num_keys, self.num_buttons, self.num_valuators, self.classes_reported))
        buf.write(xcffib.pack_list(self.buttons, "B"))
        buf.write(xcffib.pack_list(self.keys, "B"))
        buf.write(xcffib.pack_list(self.valuators, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[10] = DeviceStateNotifyEvent
class DeviceMappingNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, self.request, self.first_keycode, self.count, self.time = unpacker.unpack("xB2xBBBxI20x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 11))
        buf.write(struct.pack("=B2xBBBxI20x", self.device_id, self.request, self.first_keycode, self.count, self.time))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[11] = DeviceMappingNotifyEvent
class ChangeDeviceNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, self.time, self.request = unpacker.unpack("xB2xIB23x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 12))
        buf.write(struct.pack("=B2xIB23x", self.device_id, self.time, self.request))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[12] = ChangeDeviceNotifyEvent
class DeviceKeyStateNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, = unpacker.unpack("xB2x")
        self.keys = xcffib.List(unpacker, "B", 28)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 13))
        buf.write(struct.pack("=B2x", self.device_id))
        buf.write(xcffib.pack_list(self.keys, "B"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[13] = DeviceKeyStateNotifyEvent
class DeviceButtonStateNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.device_id, = unpacker.unpack("xB2x")
        self.buttons = xcffib.List(unpacker, "B", 28)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 14))
        buf.write(struct.pack("=B2x", self.device_id))
        buf.write(xcffib.pack_list(self.buttons, "B"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[14] = DeviceButtonStateNotifyEvent
class DeviceChange:
    Added = 0
    Removed = 1
    Enabled = 2
    Disabled = 3
    Unrecoverable = 4
    ControlChanged = 5
class DevicePresenceNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.time, self.devchange, self.device_id, self.control = unpacker.unpack("xx2xIBBH20x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 15))
        buf.write(struct.pack("=x2xIBBH20x", self.time, self.devchange, self.device_id, self.control))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[15] = DevicePresenceNotifyEvent
class DevicePropertyNotifyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.state, self.time, self.property, self.device_id = unpacker.unpack("xB2xII19xB")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 16))
        buf.write(struct.pack("=B2xII19xB", self.state, self.time, self.property, self.device_id))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[16] = DevicePropertyNotifyEvent
class ChangeReason:
    SlaveSwitch = 1
    DeviceChange = 2
class DeviceChangedEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.num_classes, self.sourceid, self.reason = unpacker.unpack("xx2xHIHHB11x")
        self.classes = xcffib.List(unpacker, DeviceClass, self.num_classes)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 1))
        buf.write(struct.pack("=x2xHIHHB11x", self.deviceid, self.time, self.num_classes, self.sourceid, self.reason))
        buf.write(xcffib.pack_list(self.classes, DeviceClass))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[1] = DeviceChangedEvent
class KeyEventFlags:
    KeyRepeat = 1 << 16
class KeyPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 2))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[2] = KeyPressEvent
class KeyReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 3))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[3] = KeyReleaseEvent
class PointerEventFlags:
    PointerEmulated = 1 << 16
class ButtonPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 4))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[4] = ButtonPressEvent
class ButtonReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 5))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[5] = ButtonReleaseEvent
class MotionEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 6))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[6] = MotionEvent
class NotifyMode:
    Normal = 0
    Grab = 1
    Ungrab = 2
    WhileGrabbed = 3
    PassiveGrab = 4
    PassiveUngrab = 5
class NotifyDetail:
    Ancestor = 0
    Virtual = 1
    Inferior = 2
    Nonlinear = 3
    NonlinearVirtual = 4
    Pointer = 5
    PointerRoot = 6
    _None = 7
class EnterEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len = unpacker.unpack("xx2xHIHBBIIIiiiiBBH")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.buttons = xcffib.List(unpacker, "I", self.buttons_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 7))
        buf.write(struct.pack("=x2xHIHBBIIIiiiiBBH", self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.buttons, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[7] = EnterEvent
class LeaveEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len = unpacker.unpack("xx2xHIHBBIIIiiiiBBH")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.buttons = xcffib.List(unpacker, "I", self.buttons_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 8))
        buf.write(struct.pack("=x2xHIHBBIIIiiiiBBH", self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.buttons, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[8] = LeaveEvent
class FocusInEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len = unpacker.unpack("xx2xHIHBBIIIiiiiBBH")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.buttons = xcffib.List(unpacker, "I", self.buttons_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 9))
        buf.write(struct.pack("=x2xHIHBBIIIiiiiBBH", self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.buttons, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[9] = FocusInEvent
class FocusOutEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len = unpacker.unpack("xx2xHIHBBIIIiiiiBBH")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.buttons = xcffib.List(unpacker, "I", self.buttons_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 10))
        buf.write(struct.pack("=x2xHIHBBIIIiiiiBBH", self.deviceid, self.time, self.sourceid, self.mode, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.same_screen, self.focus, self.buttons_len))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.buttons, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[10] = FocusOutEvent
class HierarchyMask:
    MasterAdded = 1 << 0
    MasterRemoved = 1 << 1
    SlaveAdded = 1 << 2
    SlaveRemoved = 1 << 3
    SlaveAttached = 1 << 4
    SlaveDetached = 1 << 5
    DeviceEnabled = 1 << 6
    DeviceDisabled = 1 << 7
class HierarchyInfo(xcffib.Struct):
    def __init__(self, unpacker):
        xcffib.Struct.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.attachment, self.type, self.enabled, self.flags = unpacker.unpack("HHBB2xI")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=HHBB2xI", self.deviceid, self.attachment, self.type, self.enabled, self.flags))
        return buf.getvalue()
    fixed_size = 12
class HierarchyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.flags, self.num_infos = unpacker.unpack("xx2xHIIH10x")
        self.infos = xcffib.List(unpacker, HierarchyInfo, self.num_infos)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 11))
        buf.write(struct.pack("=x2xHIIH10x", self.deviceid, self.time, self.flags, self.num_infos))
        buf.write(xcffib.pack_list(self.infos, HierarchyInfo))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[11] = HierarchyEvent
class PropertyFlag:
    Deleted = 0
    Created = 1
    Modified = 2
class PropertyEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.property, self.what = unpacker.unpack("xx2xHIIB11x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 12))
        buf.write(struct.pack("=x2xHIIB11x", self.deviceid, self.time, self.property, self.what))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[12] = PropertyEvent
class RawKeyPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 13))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[13] = RawKeyPressEvent
class RawKeyReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 14))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[14] = RawKeyReleaseEvent
class RawButtonPressEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 15))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[15] = RawButtonPressEvent
class RawButtonReleaseEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 16))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[16] = RawButtonReleaseEvent
class RawMotionEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 17))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[17] = RawMotionEvent
class TouchEventFlags:
    TouchPendingEnd = 1 << 16
    TouchEmulatingPointer = 1 << 17
class TouchBeginEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 18))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[18] = TouchBeginEvent
class TouchUpdateEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 19))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[19] = TouchUpdateEvent
class TouchEndEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIiiiiHHH2xI")
        self.mods = ModifierInfo(unpacker)
        unpacker.pad(GroupInfo)
        self.group = GroupInfo(unpacker)
        unpacker.pad("I")
        self.button_mask = xcffib.List(unpacker, "I", self.buttons_len)
        unpacker.pad("I")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 20))
        buf.write(struct.pack("=x2xHIIIIIiiiiHHH2xI", self.deviceid, self.time, self.detail, self.root, self.event, self.child, self.root_x, self.root_y, self.event_x, self.event_y, self.buttons_len, self.valuators_len, self.sourceid, self.flags))
        buf.write(self.mods.pack())
        buf.write(self.group.pack())
        buf.write(xcffib.pack_list(self.button_mask, "I"))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[20] = TouchEndEvent
class TouchOwnershipFlags:
    _None = 0
class TouchOwnershipEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.touchid, self.root, self.event, self.child, self.sourceid, self.flags = unpacker.unpack("xx2xHIIIIIH2xI8x")
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 21))
        buf.write(struct.pack("=x2xHIIIIIH2xI8x", self.deviceid, self.time, self.touchid, self.root, self.event, self.child, self.sourceid, self.flags))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[21] = TouchOwnershipEvent
class RawTouchBeginEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 22))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[22] = RawTouchBeginEvent
class RawTouchUpdateEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 23))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[23] = RawTouchUpdateEvent
class RawTouchEndEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags = unpacker.unpack("xx2xHIIHHI4x")
        self.valuator_mask = xcffib.List(unpacker, "I", self.valuators_len)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 24))
        buf.write(struct.pack("=x2xHIIHHI4x", self.deviceid, self.time, self.detail, self.sourceid, self.valuators_len, self.flags))
        buf.write(xcffib.pack_list(self.valuator_mask, "I"))
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[24] = RawTouchEndEvent
class BarrierHitEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.eventid, self.root, self.event, self.barrier, self.dtime, self.flags, self.sourceid, self.root_x, self.root_y = unpacker.unpack("xx2xHIIIIIIIH2xii")
        self.dx = FP3232(unpacker)
        unpacker.pad(FP3232)
        self.dy = FP3232(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 25))
        buf.write(struct.pack("=x2xHIIIIIIIH2xii", self.deviceid, self.time, self.eventid, self.root, self.event, self.barrier, self.dtime, self.flags, self.sourceid, self.root_x, self.root_y))
        buf.write(self.dx.pack())
        buf.write(self.dy.pack())
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[25] = BarrierHitEvent
class BarrierLeaveEvent(xcffib.Event):
    def __init__(self, unpacker):
        xcffib.Event.__init__(self, unpacker)
        base = unpacker.offset
        self.deviceid, self.time, self.eventid, self.root, self.event, self.barrier, self.dtime, self.flags, self.sourceid, self.root_x, self.root_y = unpacker.unpack("xx2xHIIIIIIIH2xii")
        self.dx = FP3232(unpacker)
        unpacker.pad(FP3232)
        self.dy = FP3232(unpacker)
        self.bufsize = unpacker.offset - base
    def pack(self):
        buf = six.BytesIO()
        buf.write(struct.pack("=B", 26))
        buf.write(struct.pack("=x2xHIIIIIIIH2xii", self.deviceid, self.time, self.eventid, self.root, self.event, self.barrier, self.dtime, self.flags, self.sourceid, self.root_x, self.root_y))
        buf.write(self.dx.pack())
        buf.write(self.dy.pack())
        buf_len = len(buf.getvalue())
        if buf_len < 32:
            buf.write(struct.pack("x" * (32 - buf_len)))
        return buf.getvalue()
_events[26] = BarrierLeaveEvent
class xinputExtension(xcffib.Extension):
    def GetExtensionVersion(self, name_len, name, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xH2x", name_len))
        buf.write(xcffib.pack_list(name, "c"))
        return self.send_request(1, buf, GetExtensionVersionCookie, is_checked=is_checked)
    def ListInputDevices(self, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2x"))
        return self.send_request(2, buf, ListInputDevicesCookie, is_checked=is_checked)
    def OpenDevice(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(3, buf, OpenDeviceCookie, is_checked=is_checked)
    def CloseDevice(self, device_id, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(4, buf, is_checked=is_checked)
    def SetDeviceMode(self, device_id, mode, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xB2x", device_id, mode))
        return self.send_request(5, buf, SetDeviceModeCookie, is_checked=is_checked)
    def SelectExtensionEvent(self, window, num_classes, classes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", window, num_classes))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(6, buf, is_checked=is_checked)
    def GetSelectedExtensionEvents(self, window, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", window))
        return self.send_request(7, buf, GetSelectedExtensionEventsCookie, is_checked=is_checked)
    def ChangeDeviceDontPropagateList(self, window, num_classes, mode, classes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIHBx", window, num_classes, mode))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(8, buf, is_checked=is_checked)
    def GetDeviceDontPropagateList(self, window, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", window))
        return self.send_request(9, buf, GetDeviceDontPropagateListCookie, is_checked=is_checked)
    def GetDeviceMotionEvents(self, start, stop, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIB", start, stop, device_id))
        return self.send_request(10, buf, GetDeviceMotionEventsCookie, is_checked=is_checked)
    def ChangeKeyboardDevice(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(11, buf, ChangeKeyboardDeviceCookie, is_checked=is_checked)
    def ChangePointerDevice(self, x_axis, y_axis, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBBx", x_axis, y_axis, device_id))
        return self.send_request(12, buf, ChangePointerDeviceCookie, is_checked=is_checked)
    def GrabDevice(self, grab_window, time, num_classes, this_device_mode, other_device_mode, owner_events, device_id, classes, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIHBBBB2x", grab_window, time, num_classes, this_device_mode, other_device_mode, owner_events, device_id))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(13, buf, GrabDeviceCookie, is_checked=is_checked)
    def UngrabDevice(self, time, device_id, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIB", time, device_id))
        return self.send_request(14, buf, is_checked=is_checked)
    def GrabDeviceKey(self, grab_window, num_classes, modifiers, modifier_device, grabbed_device, key, this_device_mode, other_device_mode, owner_events, classes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIHHBBBBBB2x", grab_window, num_classes, modifiers, modifier_device, grabbed_device, key, this_device_mode, other_device_mode, owner_events))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(15, buf, is_checked=is_checked)
    def UngrabDeviceKey(self, grabWindow, modifiers, modifier_device, key, grabbed_device, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIHBBB", grabWindow, modifiers, modifier_device, key, grabbed_device))
        return self.send_request(16, buf, is_checked=is_checked)
    def GrabDeviceButton(self, grab_window, grabbed_device, modifier_device, num_classes, modifiers, this_device_mode, other_device_mode, button, owner_events, classes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIBBHHBBBB2x", grab_window, grabbed_device, modifier_device, num_classes, modifiers, this_device_mode, other_device_mode, button, owner_events))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(17, buf, is_checked=is_checked)
    def UngrabDeviceButton(self, grab_window, modifiers, modifier_device, button, grabbed_device, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIHBBB", grab_window, modifiers, modifier_device, button, grabbed_device))
        return self.send_request(18, buf, is_checked=is_checked)
    def AllowDeviceEvents(self, time, mode, device_id, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIBB", time, mode, device_id))
        return self.send_request(19, buf, is_checked=is_checked)
    def GetDeviceFocus(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(20, buf, GetDeviceFocusCookie, is_checked=is_checked)
    def SetDeviceFocus(self, focus, time, revert_to, device_id, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIBB", focus, time, revert_to, device_id))
        return self.send_request(21, buf, is_checked=is_checked)
    def GetFeedbackControl(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(22, buf, GetFeedbackControlCookie, is_checked=is_checked)
    def ChangeFeedbackControl(self, mask, device_id, feedback_id, feedback, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIBB", mask, device_id, feedback_id))
        buf.write(feedback.pack())
        return self.send_request(23, buf, is_checked=is_checked)
    def GetDeviceKeyMapping(self, device_id, first_keycode, count, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBB", device_id, first_keycode, count))
        return self.send_request(24, buf, GetDeviceKeyMappingCookie, is_checked=is_checked)
    def ChangeDeviceKeyMapping(self, device_id, first_keycode, keysyms_per_keycode, keycode_count, keysyms, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBBB", device_id, first_keycode, keysyms_per_keycode, keycode_count))
        buf.write(xcffib.pack_list(keysyms, "I"))
        return self.send_request(25, buf, is_checked=is_checked)
    def GetDeviceModifierMapping(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(26, buf, GetDeviceModifierMappingCookie, is_checked=is_checked)
    def SetDeviceModifierMapping(self, device_id, keycodes_per_modifier, keymaps, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBx", device_id, keycodes_per_modifier))
        buf.write(xcffib.pack_list(keymaps, "B"))
        return self.send_request(27, buf, SetDeviceModifierMappingCookie, is_checked=is_checked)
    def GetDeviceButtonMapping(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(28, buf, GetDeviceButtonMappingCookie, is_checked=is_checked)
    def SetDeviceButtonMapping(self, device_id, map_size, map, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xB2x", device_id, map_size))
        buf.write(xcffib.pack_list(map, "B"))
        return self.send_request(29, buf, SetDeviceButtonMappingCookie, is_checked=is_checked)
    def QueryDeviceState(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(30, buf, QueryDeviceStateCookie, is_checked=is_checked)
    def SendExtensionEvent(self, destination, device_id, propagate, num_classes, num_events, events, classes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIBBHB3x", destination, device_id, propagate, num_classes, num_events))
        buf.write(xcffib.pack_list(events, "B"))
        buf.write(xcffib.pack_list(classes, "I"))
        return self.send_request(31, buf, is_checked=is_checked)
    def DeviceBell(self, device_id, feedback_id, feedback_class, percent, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBBb", device_id, feedback_id, feedback_class, percent))
        return self.send_request(32, buf, is_checked=is_checked)
    def SetDeviceValuators(self, device_id, first_valuator, num_valuators, valuators, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2xBBx", device_id, first_valuator, num_valuators))
        buf.write(xcffib.pack_list(valuators, "i"))
        return self.send_request(33, buf, SetDeviceValuatorsCookie, is_checked=is_checked)
    def GetDeviceControl(self, control_id, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xHBx", control_id, device_id))
        return self.send_request(34, buf, GetDeviceControlCookie, is_checked=is_checked)
    def ChangeDeviceControl(self, control_id, device_id, control, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xHBx", control_id, device_id))
        buf.write(control.pack())
        return self.send_request(35, buf, ChangeDeviceControlCookie, is_checked=is_checked)
    def ListDeviceProperties(self, device_id, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x3x", device_id))
        return self.send_request(36, buf, ListDevicePropertiesCookie, is_checked=is_checked)
    def ChangeDeviceProperty(self, property, type, device_id, format, mode, num_items, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIBBBxI", property, type, device_id, format, mode, num_items))
        return self.send_request(37, buf, is_checked=is_checked)
    def DeleteDeviceProperty(self, property, device_id, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIB3x", property, device_id))
        return self.send_request(38, buf, is_checked=is_checked)
    def GetDeviceProperty(self, property, type, offset, len, device_id, delete, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIIIBB2x", property, type, offset, len, device_id, delete))
        return self.send_request(39, buf, GetDevicePropertyCookie, is_checked=is_checked)
    def XIQueryPointer(self, window, deviceid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", window, deviceid))
        return self.send_request(40, buf, XIQueryPointerCookie, is_checked=is_checked)
    def XIWarpPointer(self, src_win, dst_win, src_x, src_y, src_width, src_height, dst_x, dst_y, deviceid, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIiiHHiiH2x", src_win, dst_win, src_x, src_y, src_width, src_height, dst_x, dst_y, deviceid))
        return self.send_request(41, buf, is_checked=is_checked)
    def XIChangeCursor(self, window, cursor, deviceid, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIH2x", window, cursor, deviceid))
        return self.send_request(42, buf, is_checked=is_checked)
    def XIChangeHierarchy(self, num_changes, changes, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xB2x", num_changes))
        buf.write(xcffib.pack_list(changes, HierarchyChange))
        return self.send_request(43, buf, is_checked=is_checked)
    def XISetClientPointer(self, window, deviceid, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", window, deviceid))
        return self.send_request(44, buf, is_checked=is_checked)
    def XIGetClientPointer(self, window, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", window))
        return self.send_request(45, buf, XIGetClientPointerCookie, is_checked=is_checked)
    def XISelectEvents(self, window, num_mask, masks, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", window, num_mask))
        buf.write(xcffib.pack_list(masks, EventMask))
        return self.send_request(46, buf, is_checked=is_checked)
    def XIQueryVersion(self, major_version, minor_version, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xHH", major_version, minor_version))
        return self.send_request(47, buf, XIQueryVersionCookie, is_checked=is_checked)
    def XIQueryDevice(self, deviceid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xH2x", deviceid))
        return self.send_request(48, buf, XIQueryDeviceCookie, is_checked=is_checked)
    def XISetFocus(self, window, time, deviceid, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIH2x", window, time, deviceid))
        return self.send_request(49, buf, is_checked=is_checked)
    def XIGetFocus(self, deviceid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xH2x", deviceid))
        return self.send_request(50, buf, XIGetFocusCookie, is_checked=is_checked)
    def XIGrabDevice(self, window, time, cursor, deviceid, mode, paired_device_mode, owner_events, mask_len, mask, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIIHBBBxH", window, time, cursor, deviceid, mode, paired_device_mode, owner_events, mask_len))
        buf.write(xcffib.pack_list(mask, "I"))
        return self.send_request(51, buf, XIGrabDeviceCookie, is_checked=is_checked)
    def XIUngrabDevice(self, time, deviceid, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIH2x", time, deviceid))
        return self.send_request(52, buf, is_checked=is_checked)
    def XIAllowEvents(self, time, deviceid, event_mode, touchid, grab_window, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIHBxII", time, deviceid, event_mode, touchid, grab_window))
        return self.send_request(53, buf, is_checked=is_checked)
    def XIPassiveGrabDevice(self, time, grab_window, cursor, detail, deviceid, num_modifiers, mask_len, grab_type, grab_mode, paired_device_mode, owner_events, mask, modifiers, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIIIHHHBBBB2x", time, grab_window, cursor, detail, deviceid, num_modifiers, mask_len, grab_type, grab_mode, paired_device_mode, owner_events))
        buf.write(xcffib.pack_list(mask, "I"))
        buf.write(xcffib.pack_list(modifiers, "I"))
        return self.send_request(54, buf, XIPassiveGrabDeviceCookie, is_checked=is_checked)
    def XIPassiveUngrabDevice(self, grab_window, detail, deviceid, num_modifiers, grab_type, modifiers, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xIIHHB3x", grab_window, detail, deviceid, num_modifiers, grab_type))
        buf.write(xcffib.pack_list(modifiers, "I"))
        return self.send_request(55, buf, is_checked=is_checked)
    def XIListProperties(self, deviceid, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xH2x", deviceid))
        return self.send_request(56, buf, XIListPropertiesCookie, is_checked=is_checked)
    def XIChangeProperty(self, deviceid, mode, format, property, type, num_items, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xHBBIII", deviceid, mode, format, property, type, num_items))
        return self.send_request(57, buf, is_checked=is_checked)
    def XIDeleteProperty(self, deviceid, property, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xH2xI", deviceid, property))
        return self.send_request(58, buf, is_checked=is_checked)
    def XIGetProperty(self, deviceid, delete, property, type, offset, len, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xHBxIIII", deviceid, delete, property, type, offset, len))
        return self.send_request(59, buf, XIGetPropertyCookie, is_checked=is_checked)
    def XIGetSelectedEvents(self, window, is_checked=True):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", window))
        return self.send_request(60, buf, XIGetSelectedEventsCookie, is_checked=is_checked)
    def XIBarrierReleasePointer(self, num_barriers, barriers, is_checked=False):
        buf = six.BytesIO()
        buf.write(struct.pack("=xx2xI", num_barriers))
        buf.write(xcffib.pack_list(barriers, BarrierReleasePointerInfo))
        return self.send_request(61, buf, is_checked=is_checked)
xcffib._add_ext(key, xinputExtension, _events, _errors)

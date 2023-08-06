# coding: utf-8

import io
import struct
import math
import sys
import base64

from .data import Tagging, Undefined

class InvalidCborError(Exception):
	pass

class _Break(InvalidCborError):
	def __init__(self):
		InvalidCborError.__init__(self, "Invalid BREAK code occurred")

class Decoder(object):
	def __init__(self, input):
		self._jump_table = [
			lambda *args: self.decode_integer(*args, sign=False),
			lambda *args: self.decode_integer(*args, sign=True),
			self.decode_bytestring,
			self.decode_textstring,
			self.decode_list,
			self.decode_dict,
			self.decode_tagging,
			self.decode_other
		]
		self.input = input

	def decode(self):
		mtype, ainfo = self._decode_ibyte()
		try:
			decoder = self._jump_table[mtype]
		except KeyError:
			raise InvalidCborError("Invalid major type {}".format(mtype))
		return decoder(mtype, ainfo)

	def decode_integer(self, mtype, ainfo, sign=False):
		res = self._decode_length(ainfo)
		if sign is True:
			return -1 - res
		else:
			return res

	def decode_bytestring(self, mtype, ainfo):
		length = self._decode_length(ainfo)
		if length is None:
			res = bytearray()
			while True:
				mtype_, ainfo_ = self._decode_ibyte()
				if (mtype_, ainfo_) == (7, 31):
					break
				if mtype_ != 2:
					pass
				res.extend(self.decode_bytestring(mtype_, ainfo_))
			return bytes(res)
		else:
			return self._read(length)

	def decode_textstring(self, mtype, ainfo):
		length = self._decode_length(ainfo)
		if length is None:
			res = bytearray()
			while True:
				mtype_, ainfo_ = self._decode_ibyte()
				if (mtype_, ainfo_) == (7, 31):
					break
				if mtype_ != 3:
					pass
				res.extend(self.decode_bytestring(mtype_, ainfo_))
			return res.decode("utf-8")
		else:
			return self._read(length).decode("utf-8")

	def decode_list(self, mtype, ainfo):
		length = self._decode_length(ainfo)
		if length is None:
			res = []
			while True:
				try:
					res.append(self.decode())
				except _Break:
					break
			return res
		else:
			res = [None for _ in range(length)]
			for n in range(length):
				res[n] = self.decode()
			return res

	def decode_dict(self, mtype, ainfo):
		length = self._decode_length(ainfo)
		if length is None:
			res = {}
			try:
				while True:
					key = self.decode()
					value = self.decode()
					res[key] = value
			except _Break:
				pass
			return res
		else:
			res = {}
			for n in range(length):
				key, value = self.decode(), self.decode()
				res[key] = value
			return res

	def decode_tagging(self, mtype, ainfo):
		length = self._decode_length(ainfo)
		return Tagging(length, self.decode())

	def decode_half_float(self, mtype, ainfo):
		half = struct.unpack(">H", self._read(2))[0]
		valu = (half & 0x7fff) << 13 | (half & 0x8000) << 16
		if ((half & 0x7c00) != 0x7c00):
			return math.ldexp(struct.unpack("!f", struct.pack("!I", valu))[0], 112)
		return struct.unpack("!f", struct.pack("!I", valu | 0x7f800000))[0]

	def decode_single_float(self, mtype, ainfo):
		return struct.unpack(">f", self._read(4))[0]

	def decode_double_float(self, mtype, ainfo):
		return struct.unpack(">d", self._read(8))[0]

	def decode_other(self, mtype, ainfo):
		if ainfo == 20:
			return False
		elif ainfo == 21:
			return True
		elif ainfo == 22:
			return None
		elif ainfo == 23:
			return Undefined
		elif ainfo == 25:
			return self.decode_half_float(mtype, ainfo)
		elif ainfo == 26:
			return self.decode_single_float(mtype, ainfo)
		elif ainfo == 27:
			return self.decode_double_float(mtype, ainfo)
		elif ainfo == 31:
			raise _Break()

	def _decode_ibyte(self):
		byte = self._read(1)[0]
		if isinstance(byte, str):
			byte = ord(byte)
		return (byte & 0b11100000) >> 5, byte & 0b00011111

	def _decode_length(self, ainfo):
		if ainfo < 24:
			return ainfo
		elif ainfo == 24:
			return from_bytes(self._read(1))
		elif ainfo == 25:
			return from_bytes(self._read(2))
		elif ainfo == 26:
			return from_bytes(self._read(4))
		elif ainfo == 27:
			return from_bytes(self._read(8))
		elif ainfo == 31:
			return None
		raise InvalidCborError("Invalid additional information {}".format(ainfo))

	def _read(self, n):
		m = self.input.read(n)
		if len(m) != n:
			raise InvalidCborError("Expected {} bytes, got {} bytes instead".format(n, len(m)))
		return m

class StandardDecoder(Decoder):
	def __init__(self, input, tagging_hooks=None):
		Decoder.__init__(self, input)
		if tagging_hooks is None:
			tagging_hooks = {}
		self.tagging_hooks = tagging_hooks
	
	def decode_tagging(self, mtype, ainfo):
		tagged = Decoder.decode_tagging(self, mtype, ainfo)
		if tagged.tag in self.tagging_hooks:
			return self.tagging_hooks[tagged.tag](tagged.tag, tagged.object)
		else:
			return tagged
	
	def register_tagging(self, tag_id, hook):
		self.tagging_hooks[tag_id] = hook

	def unregister_tagging(self, tag_id):
		del self.tagging_hooks[tag_id]
	
def load(fp, cls=Decoder, *args, **kwargs):
	return cls(fp, *args, **kwargs).decode()

def loads(data, cls=Decoder, *args, **kwargs):
	return cls(io.BytesIO(data), *args, **kwargs).decode()

def loadh(data, *args, **kwargs):
	return loads(base64.b16decode(data), *args, **kwargs)

__all__ = ["InvalidCborError", "Decoder", "load", "loads", "loadh"]

if sys.version_info[0] == 2:
    import struct
    from_formats = (None, '>B', '>H', None, '>I', None, None, None, '>Q')

    def from_bytes(val):
        return struct.unpack(from_formats[len(val)], val)[0]
else:
    def from_bytes(val):
        return int.from_bytes(val, "big")
	

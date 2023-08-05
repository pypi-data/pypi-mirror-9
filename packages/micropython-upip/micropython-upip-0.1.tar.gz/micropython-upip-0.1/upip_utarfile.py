import uctypes

# http://www.gnu.org/software/tar/manual/html_node/Standard.html
TAR_HEADER = {
    "name": (uctypes.ARRAY | 0, uctypes.UINT8 | 100),
    "size": (uctypes.ARRAY | 124, uctypes.UINT8 | 12),
}

DIRTYPE = "dir"
REGTYPE = "file"

def roundup(val, align):
    return (val + align - 1) & ~(align - 1)

def skip(f, size):
    assert size % 512 == 0
    buf = bytearray(512)
    while size:
        size -= f.readinto(buf)

class FileSection:

    def __init__(self, f, content_len, aligned_len):
        self.f = f
        self.content_len = content_len
        self.align = aligned_len - content_len

    def read(self, sz=65536):
        if self.content_len == 0:
            return b""
        if sz > self.content_len:
            sz = self.content_len
        data = self.f.read(sz)
        sz = len(data)
        self.content_len -= sz
        return data

    def skip(self):
        self.f.read(self.content_len + self.align)

class TarInfo:

    def __str__(self):
        return "TarInfo(%r, %s, %d)" % (self.name, self.type, self.size)

class TarFile:

    def __init__(self, name):
        self.f = open(name, "rb")
        self.subf = None

    def next(self):
            if self.subf:
                self.subf.skip()
            buf = self.f.read(512)
            if not buf:
                return None

            h = uctypes.struct(TAR_HEADER, uctypes.addressof(buf), uctypes.LITTLE_ENDIAN)

            # Empty block means end of archive
            if h.name[0] == 0:
                return None

            d = TarInfo()
            d.name = str(h.name, "utf-8").rstrip()
            d.size = int(bytes(h.size).rstrip(), 8)
            d.type = [REGTYPE, DIRTYPE][d.name[-1] == "/"]
            self.subf = d.subf = FileSection(self.f, d.size, roundup(d.size, 512))
            return d

    def __iter__(self):
        return self

    def __next__(self):
        v = self.next()
        if v is None:
            raise StopIteration
        return v

    def extractfile(self, tarinfo):
        return tarinfo.subf

from io import BufferedReader, TextIOWrapper
from warnings import simplefilter


def isWhiteSpace(chr: bytes) -> bool:
    return len(chr) == 1 and (
        chr == b' ' or chr == b'\t' or
        chr == b'\n' or chr == b'\r' or
        chr == b'\v' or  chr == b'\f'
    )

BUFFERSIZE = 2048
class Reader:
    def __init__(self, source_file: BufferedReader) -> None:
        self.source_file = source_file
        self.buffer = bytearray(0 for i in range(BUFFERSIZE))
        self.start_ptr = 0
        self.end_ptr = 0

    def moveToFirst(self) -> None:
        for i in range(self.end_ptr - self.start_ptr):
            self.buffer[i] = self.buffer[i + self.start_ptr]
        self.end_ptr -= self.start_ptr
        self.start_ptr = 0
    def readMore(self) -> None:
        if self.end_ptr == BUFFERSIZE:
            self.moveToFirst()
        next_chunk = self.source_file.read(BUFFERSIZE - self.end_ptr)
        self.buffer[self.end_ptr:self.end_ptr + len(next_chunk)] = next_chunk
        self.end_ptr += len(next_chunk)
    def dropWhiteSpaces(self) -> None:
        while (self.start_ptr < self.end_ptr):
            pass
    def peekToken(self) -> bytes:
        pass
    def dropToken(self) -> None:
        pass
    def takeToken(self) -> str:
        res = self.peekToken()
        self.dropToken()
        return res

if __name__ == "__main__":
    rdr = Reader(open("test1.c", "rb"))
    print(f"hello world {rdr.buffer.__len__()}")

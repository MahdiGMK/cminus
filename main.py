from io import TextIOWrapper


def isWhiteSpace(chr: bytes) -> bool:
    return len(chr) == 1 and (
        chr == b' ' or chr == b'\t' or
        chr == b'\n' or chr == b'\r' or
        chr == b'\v' or  chr == b'\f'
    )

class Reader:
    def __init__(self, source_file: TextIOWrapper) -> None:
        self.source_file = source_file
        self.buffer = bytes(0 for i in range(2048))
        self.start_ptr = 0
        self.end_ptr = 0

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
    rdr = Reader(open("test1.c"))
    print(f"hello world {rdr.buffer.__len__()}")

class FormatKey:
    public_key_header = '-----BEGIN PUBLIC KEY-----'
    pubic_key_footer = '-----END PUBLIC KEY-----'
    delimiter = '\n'

    def cut_key(self, key):
        key_length = len(key)
        line_count = key_length / 64 + 1
        out_key = self.public_key_header + self.delimiter

        for i in range(line_count):
            start = i * 64
            end = start + 64
            line = key[start:end]
            out_key += line + self.delimiter

        return out_key + self.pubic_key_footer

    def key2line(self, key):
        lines = key.split(self.delimiter)
        str = ''
        line_count = len(lines)
        for i in range(line_count - 1):
            str += lines[i] + '\\n'

        str += lines[-1]
        return str

    def cut_line(self, line):
        return line.replace('\\n', '\n')


if __name__ == '__main__':
    line_key = '''MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnxj/9qwVfgoUh/y2W89L6BkRAFljhNhgPdyPuBV64bfQNN1PjbCzkIM6qRdKBoLPXmKKMiFYnkd6rAoprih3/PrQEB/VsW8OoM8fxn67UDYuyBTqA23MML9q1+ilIZwBC2AQ2UBVOrFXfFl75p6/B5KsiNG9zpgmLCUYuLkxpLQIDAQAB'''
    fk = FormatKey()
    key = fk.cut_key(line_key)
    print key
    print fk.key2line(key)

    key ='''-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDLoh35n/z9rWqZzSqGNuVMrHv0vpby8iBFJvs7H0zZiYht39QJ
SIhkdBuVZHqrltxp6DEEhj/G/dfLyIg9AErlPmrbe6TvCfokgp8bp8ycNFw+0Oz5
aL0SGkyHXsEMT16j94IGIrYlg11xo4UkDOiEe6hOIUiR6wHmf5X0UOfVjQIDAQAB
AoGBAMbK1i56lHVmFXpeQ1RRRRrMDBrK8PvtiblYq8x06wY3cLuq1gnWCGjgvIjk
VakrlrPBXBEJqjtuVnv3oaDDp1hUn3nkNAT/iE+hPxY0dv9uD1xTYLTgmfNK3O5j
fRgxsYjce6xcp8fIsyjIF0PXmjeJoj0WzG6fyFKR3pr+hiaBAkEA7hHREZYuGHyG
cC+ql2e2zFztn0krCGXmRGFTBTGcL9nfKG6fmbQ5ttYcKqARYoaqiaIjzkAAbn+I
rLusMZl0oQJBANr4VsGx2rm/RjypjQj2fw5x3X40cdEVCr3TcpvM09ALrs47vgzz
Qi5t0tYc+8hW/scw4F83I00lWsUWYtCFDW0CQQDuAvADZiLlpjF+HZmuzyjpfgqv
UiZsufuR579plOSyzl6V/KshrxZ4Xe1BDFD1MO90tJ6ZiFEmJ+kL0IFiASqhAkBR
ydal7Ke1H6O9ftsmEOQuYguIW1Bz9zcW5kb1uNEY8XQuphP7xFThALZysUq+bvgl
MLVt+ytdYmmAGjd4iWoVAkEA1LISKq6STc5QgfQd8GOln+pafNMQ7SZ6l10vA7XC
V2AFFlCfrWl9HCNYIvN/ljIUJ4RIW1aZFLMzFv7RlfVI3w==
-----END RSA PRIVATE KEY-----'''
    line = fk.key2line(key)
    print line
    print fk.cut_line(line)

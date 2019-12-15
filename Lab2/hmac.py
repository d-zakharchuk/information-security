from Lab2.my_sha2 import MySha2Impl as Sha2
from Lab2.my_sha3 import MySha3Impl as Sha3


class Hmac:
    def __init__(self):
        self.block_size = 64
        self.o_pad = "".join(chr(x ^ 0x80) for x in range(self.block_size))
        self.i_pad = "".join(chr(x ^ 0x60) for x in range(self.block_size))

    def hmac(self, key, msg):
        sha2 = Sha2()
        sha3 = Sha3(6)

        if len(key) > self.block_size:
            key_in = sha2.sha2_algorithm(key)
            key_out = sha3.sha3_algorithm(key, padding=False)
        else:
            key_in = key + '0' * (self.block_size - len(key))
            key_out = '0' * (self.block_size - len(key)) + key

        o_key_pad = bytearray(key_out.translate(self.o_pad), encoding="utf-8")
        i_key_pad = key_in.translate(self.i_pad)
        sh2 = bytearray(sha2.sha2_algorithm(i_key_pad + msg), encoding='utf-8')
        return sha3.sha3_algorithm(bytes(o_key_pad + sh2), padding=False)

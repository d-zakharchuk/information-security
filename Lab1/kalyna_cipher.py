import sys

import numpy as np

from Lab1.s_boxes import Sboxes


class Kalyna:
    def __init__(self, block_size=128, key_length=128):
        self.BITS_IN_WORD = 64
        self.REDUCTION_POLYNOMIAL = 0x011d
        self.initialize(block_size, key_length)

    def initialize(self, block_size, key_length):
        if block_size == 128:
            self.words_in_block = int(block_size / self.BITS_IN_WORD)
            if key_length == 128:
                self.words_in_key = int(key_length / self.BITS_IN_WORD)
                self.number_of_rounds = 10
            elif key_length == 256:
                self.words_in_key = int(key_length / self.BITS_IN_WORD)
                self.number_of_rounds = 14
            else:
                raise Exception(ValueError)
        elif block_size == 256:
            self.words_in_block = int(block_size / self.BITS_IN_WORD)
            if key_length == 256:
                self.words_in_key = int(key_length / self.BITS_IN_WORD)
                self.number_of_rounds = 14
            elif key_length == 512:
                self.words_in_key = int(key_length / self.BITS_IN_WORD)
                self.number_of_rounds = 18
            else:
                raise Exception(ValueError)
        elif block_size == 512:
            self.words_in_block = int(block_size / self.BITS_IN_WORD)
            if key_length == 512:
                self.words_in_key = int(key_length / self.BITS_IN_WORD)
                self.number_of_rounds = 18
            else:
                raise Exception(ValueError)
        else:
            raise Exception(ValueError)
        self.status = np.zeros((self.words_in_block,), dtype=np.uint64)
        self.round_keys = np.zeros((self.number_of_rounds + 1, self.words_in_block), dtype=np.uint64)

    # Заміна кожного байта в шифрі з використанням SBoxes
    def sub_bytes(self):
        status_copy = bytearray(self.status)
        for i in range(self.words_in_block):
            self.status[i] = Sboxes.sboxes_enc[0][status_copy[i] & 0x00000000000000FF] | \
                             Sboxes.sboxes_enc[1][(status_copy[i] & 0x000000000000FF00) >> 8] << 8 | \
                             Sboxes.sboxes_enc[2][(status_copy[i] & 0x0000000000FF0000) >> 16] << 16 | \
                             Sboxes.sboxes_enc[3][(status_copy[i] & 0x00000000FF000000) >> 24] << 24 | \
                             Sboxes.sboxes_enc[0][(status_copy[i] & 0x000000FF00000000) >> 32] << 32 | \
                             Sboxes.sboxes_enc[1][(status_copy[i] & 0x0000FF0000000000) >> 40] << 40 | \
                             Sboxes.sboxes_enc[2][(status_copy[i] & 0x00FF000000000000) >> 48] << 48 | \
                             Sboxes.sboxes_enc[3][(status_copy[i] & 0xFF00000000000000) >> 56] << 56

    # Інвертоване перетворення за допомогою матриць SBoxes
    def inv_sub_bytes(self):
        status_copy = bytearray(self.status)
        for i in range(self.words_in_block):
            self.status[i] = Sboxes.sboxes_dec[0][status_copy[i] & 0x00000000000000FF] | \
                             Sboxes.sboxes_dec[1][(status_copy[i] & 0x000000000000FF00) >> 8] << 8 | \
                             Sboxes.sboxes_dec[2][(status_copy[i] & 0x0000000000FF0000) >> 16] << 16 | \
                             Sboxes.sboxes_dec[3][(status_copy[i] & 0x00000000FF000000) >> 24] << 24 | \
                             Sboxes.sboxes_dec[0][(status_copy[i] & 0x000000FF00000000) >> 32] << 32 | \
                             Sboxes.sboxes_dec[1][(status_copy[i] & 0x0000FF0000000000) >> 40] << 40 | \
                             Sboxes.sboxes_dec[2][(status_copy[i] & 0x00FF000000000000) >> 48] << 48 | \
                             Sboxes.sboxes_dec[3][(status_copy[i] & 0xFF00000000000000) >> 56] << 56

    @staticmethod
    def words_to_bytes(words):
        return bytearray(words)

    @staticmethod
    def bytes_to_words(length, bytes_):
        words = np.uint64(bytes_)
        if sys.byteorder != "little":
            for i in range(length):
                reversed_word = words[i][::-1]
                words[i] = reversed_word
        return words

    def shift_rows(self):
        shift = -1
        status = bytearray(self.status)
        new_status = np.zeros((self.words_in_block * 8,), dtype=np.uint64)
        for row in range(8):
            if row % (8 / self.words_in_block) == 0:
                shift += 1
            for col in range(self.words_in_block):
                new_status[row + 8 * ((col + shift) % self.words_in_block)] = status[row + 8 * col]
        self.status = (new_status.reshape((2, 8)))
        ns = np.zeros((self.words_in_block,), dtype=np.uint64)
        for i in range(self.words_in_block):
            new_list = [bytes([self.status[i][j]]) for j in range(len(self.status[i]))]
            new_list = b"".join(new_list)
            self.status[i] = int.from_bytes(new_list, byteorder=sys.byteorder)
            ns[i] = np.uint64(self.status[i][0])
        self.status = ns.copy()

    def inv_shift_rows(self):
        shift = -1
        status = bytearray(self.status)
        new_status = np.zeros((self.words_in_block * 8,), dtype=np.uint64)
        for row in range(8):
            if row % (8 / self.words_in_block) == 0:
                shift += 1
            for col in range(self.words_in_block):
                new_status[row + 8 * col] = status[row + 8 * ((col + shift) % self.words_in_block)]
        self.status = (new_status.reshape((2, 8)))
        ns = np.zeros((self.words_in_block,), dtype=np.uint64)
        for i in range(self.words_in_block):
            new_list = [bytes([self.status[i][j]]) for j in range(len(self.status[i]))]
            new_list = b"".join(new_list)
            self.status[i] = int.from_bytes(new_list, byteorder=sys.byteorder)
            ns[i] = np.uint64(self.status[i][0])
        self.status = ns.copy()

    @staticmethod
    def index(table, row, col):
        return table[row + col * 8]

    def matrix_multiply(self, matrix_):
        status = self.words_to_bytes(self.status)
        for col in range(self.words_in_block):
            result = 0
            for row in range(7, -1, -1):
                product_ = 0
                for b in range(7, -1, -1):
                    product_ ^= self.multiply_gf(status[b + 8 * col], matrix_[row][b])
                result |= product_ << (row * 8)
            self.status[col] = np.uint64(result)

    def multiply_gf(self, x, y):
        r = 0
        for i in range(8):
            if (y & 0x1) == 1:
                r ^= x
            h_bit = x & 0x80
            x <<= 1
            if h_bit == 0x80:
                x ^= self.REDUCTION_POLYNOMIAL
            y >>= 1
        return r

    def mix_columns(self):
        self.matrix_multiply(Sboxes.mds_matrix)

    def encipher_round(self):
        self.sub_bytes()
        self.shift_rows()
        self.mix_columns()

    def xor_round_key(self, round_):
        for i in range(self.words_in_block):
            self.status[i] ^= self.round_keys[round_][i]

    def xor_round_key_expand(self, value_):
        for i in range(self.words_in_block):
            self.status[i] ^= value_[i]

    def rotate_left(self, size, value_):
        rotate_bytes = 2 * size + 3
        bytes_num = size * (self.BITS_IN_WORD / 8)
        bytes_ = self.words_to_bytes(value_)
        buffer = bytes_[:rotate_bytes]
        new_bytes_index = int(bytes_num - rotate_bytes)
        bytes_[new_bytes_index - 1:] = buffer
        return self.bytes_to_words(bytes_num, bytes_)

    @staticmethod
    def shift_left(size, value_):
        value_ = bytearray(value_)
        for i in range(size):
            value_[i] <<= 1
        return np.uint64(value_)

    @staticmethod
    def rotate(size, value_):
        temp = value_[0]
        for i in range(1, size):
            value_[i - 1] = value_[i]
        value_[size - 1] = temp
        return value_

    def add_round_key(self, round_):
        for i in range(self.words_in_block):
            self.status[i] += self.round_keys[round_][i]

    def add_round_key_expand(self, value_):
        for i in range(self.words_in_block):
            self.status[i] += value_[i]

    def key_expand_kt(self, key):
        self.status[0] += self.words_in_block + self.words_in_key + 1
        if self.words_in_block == self.words_in_key:
            k0 = key.copy()
            k1 = key.copy()
        else:
            k0 = key.copy()
            k1 = key + self.words_in_block
        self.add_round_key_expand(k0)
        self.encipher_round()
        self.xor_round_key_expand(k1)
        self.encipher_round()
        self.add_round_key_expand(k0)
        self.encipher_round()
        kt = self.status.copy()
        return kt

    def key_expand_even(self, key, kt):
        initial = np.zeros((self.words_in_key * 8,), dtype=np.uint64)
        kt_round = np.zeros((self.words_in_block * 8,), dtype=np.uint64)
        tmv = np.zeros((self.words_in_block * 8,), dtype=np.uint64)
        round_ = 0
        initial = key.copy()
        for i in range(self.words_in_block):
            tmv[i] = 0x0001000100010001
        while True:
            self.status = kt.copy()
            self.add_round_key_expand(tmv)
            kt_round = self.status.copy()
            self.status = initial.copy()
            self.add_round_key_expand(kt_round)
            self.encipher_round()
            self.xor_round_key_expand(kt_round)
            self.encipher_round()
            self.add_round_key_expand(kt_round)
            self.round_keys[round_] = self.status.copy()
            if self.words_in_key == round_:
                break
            if self.words_in_key != self.words_in_block:
                round_ += 2
                tmv = self.shift_left(self.words_in_block, tmv)
                self.status = kt.copy()
                self.add_round_key_expand(tmv)
                kt_round = self.status.copy()
                self.status = initial + self.words_in_block
                self.add_round_key_expand(kt_round)
                self.encipher_round()
                self.xor_round_key_expand(kt_round)
                self.encipher_round()
                self.add_round_key_expand(kt_round)
                self.round_keys[round_] = self.status.copy()
                if self.number_of_rounds == round_:
                    break
            round_ += 2
            tmv = self.shift_left(self.words_in_block, tmv)
            initial = self.rotate(self.words_in_key, initial)

    def key_expand_odd(self):
        for i in range(1, self.number_of_rounds, 2):
            self.round_keys[i] = self.round_keys[i - 1].copy()
            self.rotate_left(self.words_in_block, self.round_keys[i])

    def kalyna_key_expand(self, key):
        kt = self.key_expand_kt(key)
        self.key_expand_even(key, kt)
        self.key_expand_odd()

    def kalyna_encipher(self, plaintext):
        round_ = 0
        self.status = plaintext.copy()
        self.add_round_key(round_)
        for i in range(1, self.number_of_rounds):
            self.encipher_round()
            self.xor_round_key(round_)
        self.encipher_round()
        self.add_round_key(self.number_of_rounds)
        return self.status.copy()

    def kalyna_decipher(self, cipher_text):
        round_ = self.number_of_rounds
        self.status = cipher_text.copy()
        self.sub_round_key(round_)
        for round_ in range(self.number_of_rounds - 1, 0, -1):
            self.decipher_round()
            self.xor_round_key(round_)
        self.decipher_round()
        self.sub_round_key(0)
        return self.status.copy()

    def sub_round_key(self, round_):
        for i in range(self.words_in_key):
            self.status[i] -= self.round_keys[round_][i]

    def decipher_round(self):
        self.inv_mix_columns()
        self.inv_shift_rows()
        self.inv_sub_bytes()

    def inv_mix_columns(self):
        self.matrix_multiply(Sboxes.mds_inv_matrix)

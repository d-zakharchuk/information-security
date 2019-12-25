import sys

import numpy as np


class MySha3Impl:
    def __init__(self, L):
        self.L = L
        self.num_of_bits = 2 ** L
        self.keccak_f = self.num_of_bits * 5 * 5
        self.num_of_rounds = 12 + 2 * L

    @staticmethod
    def convert_to_bin(data):
        data = bytearray(data)
        binary_string = "{:08b}".format(int(data.hex(), 16))
        return [int(c) for c in binary_string]

    @staticmethod
    def convert_to_hex_string(data):
        data = "".join([str(x) for x in data])
        a1 = hex(int(data, 2))[2:]
        return a1

    # Конвертація у 3D масив
    def convert_1d_to_3d(self, old_array):
        new_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    new_array[i][j][k] = old_array[self.num_of_bits * (5 * j + i) + k]
        return new_array

    # 3D масив до масиву 1D
    def convert_3d_to_1d(self, old_array):
        new_array = np.zeros(shape=self.keccak_f, dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    new_array[self.num_of_bits * (5 * j + i) + k] = old_array[i][j][k]
        return new_array

    # theta-функція
    def theta_calc(self, input_array, i, j, k):
        # output[i][j][k] = input[i][j][k] XOR SUM1 XOR SUM2
        # SUM1
        a = np.bitwise_xor(input_array[(i - 1) % 5][0][k], input_array[(i - 1) % 5][1][k])
        b = np.bitwise_xor(input_array[(i - 1) % 5][2][k], input_array[(i - 1) % 5][3][k])
        c = np.bitwise_xor(a, b)
        first = np.bitwise_xor(c, input_array[(i - 1) % 5][4][k])
        # SUM2
        d = np.bitwise_xor(input_array[(i + 1) % 5][0][(k - 1) % self.num_of_bits],
                           input_array[(i + 1) % 5][1][(k - 1) % self.num_of_bits])
        e = np.bitwise_xor(input_array[(i + 1) % 5][2][(k - 1) % self.num_of_bits],
                           input_array[(i + 1) % 5][3][(k - 1) % self.num_of_bits])
        f = np.bitwise_xor(d, e)
        second = np.bitwise_xor(f, input_array[(i + 1) % 5][4][(k - 1) % self.num_of_bits])
        return np.bitwise_xor(first, second)

    # theta-функція
    def theta(self, input_array):
        output_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    output_array[i][j][k] = np.bitwise_xor(input_array[i][j][k],
                                                           self.theta_calc(input_array, i, j, k))
        return output_array

    # Rho
    def rho(self, ain):
        matrix_rho = np.array([
            [0, 36, 3, 41, 18],
            [1, 44, 10, 45, 2],
            [62, 6, 43, 15, 61],
            [28, 55, 25, 21, 56],
            [27, 20, 39, 8, 14]
        ], dtype=int)
        output_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    select = matrix_rho[i][j] % self.num_of_bits  # вибір (t + 1)(t + 2)/2 через матрицю matrix_rho
                    output_array[i][j][k] = ain[i][j][k - select]
        return output_array

    # Pi
    def pi(self, ain):
        output_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    output_array[j][(2 * i + 3 * j) % 5][k] = ain[i][j][k]
        return output_array

    # ksi
    def ksi(self, ain):
        output_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    xor = np.bitwise_xor(ain[(i + 1) % 5][j][k], 1)
                    mul = xor * (ain[(i + 2) % 5][j][k])
                    output_array[i][j][k] = np.bitwise_xor(ain[i][j][k], mul)
        return output_array

    # Iota
    def iota(self, ain, rnd):
        output_array = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        bit = np.zeros(shape=(5, 5, self.num_of_bits), dtype=int)
        rc = np.zeros(shape=self.num_of_rounds * (self.L + 1), dtype=int)  # 24 * 7
        w = np.array([1, 0, 0, 0, 0, 0, 0, 0], dtype=int)
        rc[0] = w[0]
        for i in range(1, (self.L + 1) * self.num_of_rounds):  # 24 * 7
            a = np.bitwise_xor(w[0], w[4])
            b = np.bitwise_xor(w[5], w[6])
            tail = np.bitwise_xor(a, b)
            w = [w[1], w[2], w[3], w[4], w[5], w[6], w[7], tail]
            rc[i] = w[0]
        for l in range(self.L + 1):
            q = pow(2, l) - 1
            t = l + (self.L + 1) * rnd
            bit[0][0][q] = rc[t]
        for i in range(5):
            for j in range(5):
                for k in range(self.num_of_bits):
                    output_array[i][j][k] = np.bitwise_xor(ain[i][j][k], bit[i][j][k])
        return output_array

    def sha3_algorithm(self, pt, padding=True):
        if isinstance(pt, bytes):
            pt = self.convert_to_bin(pt)
        input_array = np.array(pt, dtype=int)
        size = input_array.size
        input_array.resize(self.keccak_f, refcheck=False)
        if padding:
            if size > 1086:
                sys.exit("Input must be less than or equal to 1086 bits")
            input_array[size] = 1
            input_array[1087] = 1
        output_array = self.convert_1d_to_3d(input_array)
        for rounds in range(self.num_of_rounds):
            output_array = self.iota(self.ksi(self.pi(self.rho(self.theta(output_array)))), rounds)
        output_array = self.convert_3d_to_1d(output_array)
        return self.convert_to_hex_string(output_array)

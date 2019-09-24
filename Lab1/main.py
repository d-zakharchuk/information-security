import numpy as np

from Lab1.kalyna_cipher import Kalyna


def main():
    ke = Kalyna(block_size=128, key_length=128)  # екземпляр класу для шифрування
    kd = Kalyna(block_size=128, key_length=128)  # екземпляр класу для дешифрування
    pt22_e = np.uint64(np.array([0x1716151413121110, 0x1f1e1d1c1b1a1918]))  # plain-text
    key22_e = np.uint64(np.array([0x0706050403020100, 0x0f0e0d0c0b0a0908]))  # ключ шифрування
    expect22_e = np.uint64(np.array([0x20ac9b777d1cbf81, 0x06add2b439eac9e1]))

    ct22_d = np.uint64(np.array([0x18191a1b1c1d1e1f, 0x1011121314151617]))  # шифротекст для розшифровки
    key22_d = np.uint64(np.array([0x08090a0b0c0d0e0f, 0x0001020304050607]))  # ключ дешифрування
    expect22_d = np.uint64(np.array([0x84c70c472bef9172, 0xd7da733930c2096f]))

    ke.kalyna_key_expand(key22_e)
    print("=============")
    print("Kalyna ", np.uint64(ke.words_in_block * 64), np.uint64(ke.words_in_key * 64))
    print("--- ENCIPHERING ---")
    print("Key:")
    print(bytes(key22_e).hex().upper())
    print("Plaintext:")
    print(bytes(pt22_e).hex().upper())
    ct22_e = ke.kalyna_encipher(pt22_e)
    print("Ciphertext:")
    print(bytes(ct22_e).hex().upper())
    print("Expected:")
    print(bytes(expect22_e).hex().upper())
    ke.kalyna_key_expand(key22_d)
    print("=============")
    print("Kalyna ", np.uint64(kd.words_in_block * 64), np.uint64(kd.words_in_key * 64))
    print("--- DECIPHERING ---")
    print("Key:")
    print(bytes(key22_d).hex().upper())
    print("Ciphertext:")
    print(bytes(ct22_d).hex().upper())
    pt22_d = kd.kalyna_decipher(ct22_d)
    print("Plaintext:")
    print(bytes(pt22_d).hex().upper())
    print("Expected:")
    print(bytes(expect22_d).hex().upper())


if __name__ == "__main__":
    main()

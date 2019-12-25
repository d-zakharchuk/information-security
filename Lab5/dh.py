import random
import sys

import numpy as np
from bitstring import BitArray

from Lab1.kalyna_cipher import Kalyna
from Lab2.hmac import Hmac
from Lab3.rsa import RsaImpl
from Lab4.ec import EllipticCurve
from Lab4.variant import Variant


class DiffieHellman:
    def __init__(self):
        self.ec = EllipticCurve(Variant.var11)
        self.h = Hmac()

    @staticmethod
    def generate_n_bit_number(n):
        return random.randint(pow(2, n - 1), pow(2, n) - 1)

    @staticmethod
    def rsa_keys(r):
        p = random.randint(10 ** 150, 10 ** 151)
        while not r.fermat_test(p):
            p += 1
        q = random.randint(10 ** 150, 10 ** 151)
        while not r.fermat_test(q):
            q += 1
        public, private = r.generate_key_pair(p, q)
        return public, private

    @staticmethod
    def kalyna_encrypt(pt, key):
        key = BitArray(key.to_bytes(16, sys.byteorder))
        key_ = np.uint64(np.array(key.unpack('uintle:64, uintle:64')))
        pt = BitArray(bytearray(pt, encoding='utf-8'))
        fm = ", ".join(['uintle:64'] * (pt.len // 64))
        pt_ = np.uint64(np.array(pt.unpack(fm)))
        cipher = []
        for i in range(0, len(pt_), 2):
            k = Kalyna()
            k.kalyna_key_expand(key_)
            if i == len(pt_) - 1:
                pt_s = np.uint64(np.array([pt_[i], 0x0]))
            else:
                pt_s = np.uint64(np.array([pt_[i], pt_[i + 1]]))
            cipher.extend(k.kalyna_encipher(pt_s))
        return cipher

    @staticmethod
    def kalyna_decrypt(ct_, key):
        key = BitArray(key.to_bytes(16, sys.byteorder))
        key_ = np.uint64(np.array(key.unpack('uintle:64, uintle:64')))
        plain = []
        for i in range(0, len(ct_), 2):
            k = Kalyna()
            k.kalyna_key_expand(key_)
            if i == len(ct_) - 1:
                ct_s = np.uint64(np.array([ct_[i], 0x0]))
            else:
                ct_s = np.uint64(np.array([ct_[i], ct_[i + 1]]))
            plain.extend(k.kalyna_decipher(ct_s))
        result = bytes(np.uint64(np.array(plain))).decode('utf-8')
        return result.split(' ')[:4]

    @staticmethod
    def verify(message, private, public):
        r = RsaImpl()
        encrypted_msg = r.encrypt(private, message, verbose=False)
        dec = r.decrypt(public, encrypted_msg, verbose=False)
        return dec == message

    @staticmethod
    def print_results(parameters):
        secret_key_b, secret_key_a, b, a, check_bob_key, check_alice_key, check_bob_id, check_alice_id = parameters
        print("Bob's secret key: {}".format(secret_key_b))
        print("Alice's secret key: {}".format(secret_key_a))
        print("Bob's common key: {}".format(b.print()))
        print("Alice's common key: {}".format(a.print()))
        print("Keys are equal: {}".format(b.print() == a.print()))
        print("Bob's key verification: {}".format(check_bob_key))
        print("Alice's key verification: {}".format(check_alice_key))
        print("Bob's id verification: {}".format(check_bob_id))
        print("Alice's id verification: {}".format(check_alice_id))
        print()

    def signed(self, p=None, q=None, msg=None):
        if msg is None:
            msg = int(str(p.x) + str(p.y) + str(q.x) + str(q.y)) % self.ec.fx
        r = RsaImpl()
        public, private = self.rsa_keys(r)
        return public, private, r.hash_function(str(msg)), str(msg)

    def sigma_basic(self):
        print("Sigma basic")
        g = self.ec.generate_point(n=1)[0]
        km = self.generate_n_bit_number(16)
        km = "".join([str(x) for x in self.ec.convert_int_to_polynomial(km)])
        secret_key_a = self.generate_n_bit_number(32)
        secret_key_b = self.generate_n_bit_number(32)
        # Alice to Bob: g^x
        gx = self.ec.k_point(secret_key_a, g)

        # Bob to Alice: g^y, B, SIG_B(g^x, g^y), MAC_km(B)
        gy = self.ec.k_point(secret_key_b, g)
        b = self.ec.k_point(secret_key_b, gx)
        pub_b, pr_b, sign_b, msg_b = self.signed(gx, gy)
        alice = "Alice"
        bob = "Bob"
        mac_b = self.h.hmac(km, bob)

        # Alice to Bob: A, SIG_A(g^y, g^x), MAC_km(A)
        a = self.ec.k_point(secret_key_a, gy)
        check_bob_key = self.verify(sign_b, pr_b, pub_b)
        check_bob_id = self.h.hmac(km, bob) == mac_b
        pub_a, pr_a, sign_a, msg_a = self.signed(gy, gx)
        mac_a = self.h.hmac(km, alice)
        check_alice_id = self.h.hmac(km, alice) == mac_a
        check_alice_key = self.verify(sign_a, pr_a, pub_a)
        parameters = [secret_key_b, secret_key_a, b, a, check_bob_key, check_alice_key, check_bob_id, check_alice_id]
        self.print_results(parameters)

    def sigma_i(self):
        print("Sigma I")
        g = self.ec.generate_point(n=1)[0]
        km = self.generate_n_bit_number(32)
        km = "".join([str(x) for x in self.ec.convert_int_to_polynomial(km)])
        key_encrypt = self.generate_n_bit_number(128)
        secret_key_a = self.generate_n_bit_number(32)
        secret_key_b = self.generate_n_bit_number(32)
        # Alice to Bob: g^x
        gx = self.ec.k_point(secret_key_a, g)

        # Bob to Alice: g^y, B, SIG_B(g^x, g^y), MAC_km(B)
        gy = self.ec.k_point(secret_key_b, g)
        b = self.ec.k_point(secret_key_b, gx)
        pub_b, pr_b, sign_b, msg_b = self.signed(gx, gy)
        alice = "Alice"
        bob = "Bob"
        mac_b = self.h.hmac(km, bob)
        msg_to_encrypt_bob = " ".join([bob, msg_b, sign_b, mac_b])
        encrypt_bob = self.kalyna_encrypt(msg_to_encrypt_bob, key_encrypt)

        # Alice to Bob: {A, SIG_A(g^y, g^x), MAC_km(A)}_k_enc
        a = self.ec.k_point(secret_key_a, gy)
        retrieve_bob, signed_msg_retrieve_bob, signed_b_sign_retrieve, mac_retrieve_bob = \
            self.kalyna_decrypt(encrypt_bob, key_encrypt)
        pub_b, pr_b, sign_b, msg_b = self.signed(msg=signed_msg_retrieve_bob)
        check_bob_key = self.verify(sign_b, pr_b, pub_b)
        check_bob_id = self.h.hmac(km, bob) == mac_retrieve_bob
        pub_a, pr_a, sign_a, msg_a = self.signed(gy, gx)
        mac_a = self.h.hmac(km, alice)
        msg_to_encrypt_alice = " ".join([alice, msg_a, sign_a, mac_a])
        encrypt_alice = self.kalyna_encrypt(msg_to_encrypt_alice, key_encrypt)
        retrieve_alice, signed_msg_retrieve_alice, signed_a_sign_retrieve, mac_retrieve_alice = \
            self.kalyna_decrypt(encrypt_alice, key_encrypt)
        pub_a, pr_a, sign_a, msg_a = self.signed(msg=signed_msg_retrieve_alice)
        check_alice_key = self.verify(sign_a, pr_a, pub_a)
        check_alice_id = self.h.hmac(km, alice) == mac_retrieve_alice
        parameters = [secret_key_b, secret_key_a, b, a, check_bob_key, check_alice_key, check_bob_id, check_alice_id]
        self.print_results(parameters)

    def sigma_r(self):
        print("Sigma R")
        g = self.ec.generate_point(n=1)[0]
        km1 = self.generate_n_bit_number(32)
        km1 = "".join([str(x) for x in self.ec.convert_int_to_polynomial(km1)])
        km2 = self.generate_n_bit_number(32)
        km2 = "".join([str(x) for x in self.ec.convert_int_to_polynomial(km2)])
        key_encrypt1 = self.generate_n_bit_number(128)
        key_encrypt2 = self.generate_n_bit_number(128)
        secret_key_a = self.generate_n_bit_number(32)
        secret_key_b = self.generate_n_bit_number(32)

        # Alice to Bob: g^x
        gx = self.ec.k_point(secret_key_a, g)

        # Bob to Alice: g^y
        gy = self.ec.k_point(secret_key_b, g)
        a = self.ec.k_point(secret_key_a, gy)
        b = self.ec.k_point(secret_key_b, gx)

        # Alice to Bob: {A, SIG_A(g^y, g^x), MAC_km1(A)}_k_enc1
        pub_a, pr_a, sign_a, msg_a = self.signed(gy, gx)
        alice = "Alice"
        bob = "Bob"
        mac_a = self.h.hmac(km1, alice)
        msg_to_encrypt_alice = " ".join([alice, msg_a, sign_a, mac_a])
        encrypt_alice = self.kalyna_encrypt(msg_to_encrypt_alice, key_encrypt1)

        # Bob to Alice: {B, SIG_B(g^x, g^y), MAC_km(A)}_ke
        retrieve_alice, signed_msg_retrieve_alice, signed_a_sign_retrieve, mac_retrieve_alice = \
            self.kalyna_decrypt(encrypt_alice, key_encrypt1)
        check_alice_key = self.verify(sign_a, pr_a, pub_a)
        check_alice_id = self.h.hmac(km1, alice) == mac_retrieve_alice
        pub_b, pr_b, sign_b, msg_b = self.signed(gx, gy)
        mac_b = self.h.hmac(km2, bob)
        msg_to_encrypt_bob = " ".join([bob, msg_b, sign_b, mac_b])
        encrypt_bob = self.kalyna_encrypt(msg_to_encrypt_bob, key_encrypt2)
        retrieve_bob, signed_msg_retrieve_bob, signed_b_sign_retrieve, mac_retrieve_bob = \
            self.kalyna_decrypt(encrypt_bob, key_encrypt2)
        check_bob_key = self.verify(sign_b, pr_b, pub_b)
        check_bob_id = self.h.hmac(km2, bob) == mac_retrieve_bob
        parameters = [secret_key_b, secret_key_a, b, a, check_bob_key, check_alice_key, check_bob_id, check_alice_id]
        self.print_results(parameters)

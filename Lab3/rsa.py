import random

from Lab2.my_sha2 import MySha2Impl


class RsaImpl:
    @staticmethod
    def co_prime(a, b):
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def extended_gcd(aa, bb):
        # розширений алгоритм Евкліда
        prev_remainder, remainder = abs(aa), abs(bb)
        x, prev_x, y, prev_y = 0, 1, 1, 0
        while remainder:
            prev_remainder, (quotient, remainder) = remainder, divmod(prev_remainder, remainder)
            x, prev_x = prev_x - quotient * x, x
            y, prev_y = prev_y - quotient * y, y
        return prev_remainder, prev_x * (-1 if aa < 0 else 1), prev_y * (-1 if bb < 0 else 1)

    # Знаходження оберненого числа за модулем m
    def mod_inv(self, a, m):
        g, x, y = self.extended_gcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        return x % m

    @staticmethod
    # Тест Ферма для простих чисел
    def fermat_test(n, k=128):
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(k):
            a = random.randint(1, n - 1)
            if pow(a, n - 1, n) != 1:
                return False
        return True

    def generate_key_pair(self, p, q):
        n = p * q
        phi = (p - 1) * (q - 1)
        # public key
        e = random.randrange(1, phi)
        # перевірка, чи gcd(e, phi) == 1
        g = self.co_prime(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = self.co_prime(e, phi)
        # private key
        d = self.mod_inv(e, phi)
        # Public key: (e, n); private key: (d, n)
        return (e, n), (d, n)

    @staticmethod
    def encrypt(private_key, plaintext):
        key, n = private_key
        # Кожна літера конвертується в число (ASCII-код), потім обчислюється a^key mod n
        number_representation = [ord(char) for char in plaintext]
        print("Number representation before encryption: ", number_representation)
        cipher = [pow(ord(char), key, n) for char in plaintext]
        return cipher

    @staticmethod
    def decrypt(public_key, cipher_text):
        key, n = public_key
        # Шифр розшифровується у числовому представленні
        number_representation = [pow(char, key, n) for char in cipher_text]
        # потім замість чисел підставляються відповідні їм char-символи
        plain = [chr(pow(char, key, n)) for char in cipher_text]
        print("Decrypted number representation : ", number_representation)
        return ''.join(plain)

    @staticmethod
    def hash_function(message):
        s = MySha2Impl()
        hashed = s.sha2_algorithm(message)
        return hashed

    def verify(self, received_hash, message):
        my_hash = self.hash_function(message)
        if received_hash == my_hash:
            print("Verification successful: ", )
            print(received_hash, " = ", my_hash)
        else:
            print("Verification failed")
            print(received_hash, " != ", my_hash)

    def run_rsa(self):
        p = random.randint(10 ** 100, 10 ** 101)
        while not self.fermat_test(p):
            p += 1
        q = random.randint(10 ** 100, 10 ** 101)
        while not self.fermat_test(q):
            q += 1
        print("Generating key pairs ...")
        public, private = self.generate_key_pair(p, q)
        print("Public key: ", public)
        print("Private key: ", private)
        message = input("Enter a message: ")
        hashed = self.hash_function(message)
        encrypted_msg = self.encrypt(private, hashed)
        print("Encrypted hashed message:")
        print(''.join(map(lambda x: str(x), encrypted_msg)))
        print()
        decrypted_msg = self.decrypt(public, encrypted_msg)
        print("Decrypted message:")
        print(decrypted_msg)
        print()
        print("Verification process . . .")
        self.verify(decrypted_msg, message)

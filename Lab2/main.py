import hashlib

from Lab2.my_sha2 import MySha2Impl
from Lab2.my_sha3 import MySha3Impl


def main():
    le = 6
    sha3_aaa = MySha3Impl(le)
    sha2_aaa = MySha2Impl()

    my_input = b"data"
    sha3_output = sha3_aaa.sha3_algorithm(my_input, padding=False)
    print(sha3_output)

    sha2_output = sha2_aaa.sha2_algorithm(sha3_output)
    print(sha2_output)
    print("")
    a = ""
    result = hashlib.sha256(a.encode())
    print(result.hexdigest())
    print(sha2_aaa.sha2_algorithm(a))


if __name__ == '__main__':
    main()

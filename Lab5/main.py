from Lab5.dh import DiffieHellman


def main():
    dh = DiffieHellman()
    dh.sigma_basic()
    dh.sigma_i()
    dh.sigma_r()


if __name__ == '__main__':
    main()

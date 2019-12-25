import time

from Lab4.ec import EllipticCurve, Point
from Lab4.variant import Variant


def example(e_, p, q):
    print("P =", p.print())
    print("Q =", q.print())

    start = time.process_time()
    r = e_.add_points(p, q)
    end = time.process_time()
    print("P + Q =", r.print())
    print("{0} s\n".format(end - start))

    start = time.process_time()
    r = e_.add_points(q, p)
    end = time.process_time()
    print("Q + P =", r.print())
    print("{0} s\n".format(end - start))

    start = time.process_time()
    r2 = e_.add_points(p, p)
    end = time.process_time()
    print("2P =", r2.print())
    print("{0} s\n".format(end - start))

    start = time.process_time()
    r3 = e_.add_points(q, q)
    end = time.process_time()
    print("2Q =", r3.print())
    print("{0} s\n".format(end - start))

    # start = time.process_time_ns()
    # k = e_.logarithm(p, q)
    # end = time.process_time_ns()
    # print("kQ = P; k =", k)
    # print("{0} ns\n".format(end - start))
    k = 10
    start = time.process_time()
    r4 = e_.k_point(k, q)
    end = time.process_time()
    print("{0}Q = {1}".format(k, r4.print()))
    print("{0} s\n".format(end - start))
    print(80 * "-")


def main():
    e_ = EllipticCurve(Variant.var1)
    # p, q = e_.generate_point(n=2)
    # example(e_, p, q)

    x = e_.parse_value_b("72D867F93A93AC27DF9FF01AFFE74885C8C540420")
    y = e_.parse_value_b("0224A9C3947852B97C5599D5F4AB81122ADC3FD9B")
    x2 = e_.parse_value_b("057DE7FDE023FF929CB6AC785CE4B79CF64ABD2DA")
    y2 = e_.parse_value_b("3E85444324BCF06AD85ABF6AD7B5F34770532B9AA")
    p = Point(x, y)
    q = Point(x2, y2)
    example(e_, p, q)

    px = e_.parse_value_fx([8, 5, 3, 1])
    py = e_.parse_value_fx([8, 4, 1, 0])
    qx = e_.parse_value_fx([8, 6, 2, 0])
    qy = e_.parse_value_fx([7, 5, 4, 1, 0])
    tx = e_.parse_value_fx([6, 4, 3, 1])
    ty = e_.parse_value_fx([5, 0])

    p = Point(x=px, y=py)
    q = Point(x=qx, y=qy)
    example(e_, p, q)

    p = Point(x=px, y=py)
    q = Point(x=tx, y=ty)
    example(e_, p, q)


if __name__ == "__main__":
    main()

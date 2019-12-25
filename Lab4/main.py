import time

from Lab4.ec import EllipticCurve, Point
from Lab4.variant import Variant


def example(e_, p, q):
    print("P =", p.print())
    print("Q =", q.print())

    start = time.process_time_ns()
    r = e_.add_points(p, q)
    end = time.process_time_ns()
    print("P + Q =", r.print())
    print("{0} ns\n".format(end - start))

    start = time.process_time_ns()
    r2 = e_.add_points(p, p)
    end = time.process_time_ns()
    print("2P =", r2.print())
    print("{0} ns\n".format(end - start))

    start = time.process_time_ns()
    r3 = e_.add_points(q, q)
    end = time.process_time_ns()
    print("2Q =", r3.print())
    print("{0} ns\n".format(end - start))

    start = time.process_time_ns()
    k = e_.logarithm(p, q)
    end = time.process_time_ns()
    print("kQ = P; k =", k)
    print("{0} ns\n".format(end - start))

    start = time.process_time_ns()
    r4 = e_.k_point(k, q)
    end = time.process_time_ns()
    print("{0}Q = {1}".format(k, r4.print()))
    print("{0} ns\n".format(end - start))
    print(80 * "-")


def main():
    e_ = EllipticCurve(Variant.var1)
    p, q = e_.generate_point(n=2)
    example(e_, p, q)

    x = e_.parse_value_b("72D867F93A93AC27DF9FF01AFFE74885C8C540420")
    y = e_.parse_value_b("0224A9C3947852B97C5599D5F4AB81122ADC3FD9B")
    x2 = e_.parse_value_b("057DE7FDE023FF929CB6AC785CE4B79CF64ABD2DA")
    y2 = e_.parse_value_b("3E85444324BCF06AD85ABF6AD7B5F34770532B9AA")
    p = Point(x, y)
    q = Point(x2, y2)
    example(e_, p, q)


if __name__ == "__main__":
    main()

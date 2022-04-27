def swap2_profit_ether(a_0, b_0, b_1, w_0, w_1, f_0, b_2, b_3, w_2, w_3, f_1):
    return -a_0 + 1.0e-18 * b_3 * (
        1
        - (
            b_2
            / (
                1.0
                * b_1
                * f_1
                * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                + b_2
            )
        )
        ** (w_2 / w_3)
    )


def swap2_profit_ether_d_a0(a_0, b_0, b_1, w_0, w_1, f_0, b_2, b_3, w_2, w_3, f_1):
    return (
        1.0e-36
        * b_1
        * b_3
        * f_0
        * f_1
        * w_0
        * w_2
        * (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1)
        * (
            b_2
            / (
                1.0
                * b_1
                * f_1
                * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                + b_2
            )
        )
        ** (w_2 / w_3)
        * (1.0e18 * a_0 * f_0 + b_0)
        / (
            w_1
            * w_3
            * (a_0 * f_0 + 1.0e-18 * b_0) ** 2
            * (
                1.0
                * b_1
                * f_1
                * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                + b_2
            )
        )
        - 1
    )


def swap3_profit_ether(
    a_0, b_0, b_1, w_0, w_1, f_0, b_2, b_3, w_2, w_3, f_1, b_4, b_5, w_4, w_5, f_2
):
    return -a_0 + 1.0e-18 * b_5 * (
        1
        - (
            b_4
            / (
                1.0
                * b_3
                * f_2
                * (
                    1
                    - (
                        b_2
                        / (
                            1.0
                            * b_1
                            * f_1
                            * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                            + b_2
                        )
                    )
                    ** (w_2 / w_3)
                )
                + b_4
            )
        )
        ** (w_4 / w_5)
    )


def swap3_profit_ether_d_a0(
    a_0, b_0, b_1, w_0, w_1, f_0, b_2, b_3, w_2, w_3, f_1, b_4, b_5, w_4, w_5, f_2
):
    return (
        1.0e-36
        * b_1
        * b_3
        * b_5
        * f_0
        * f_1
        * f_2
        * w_0
        * w_2
        * w_4
        * (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1)
        * (
            b_2
            / (
                1.0
                * b_1
                * f_1
                * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                + b_2
            )
        )
        ** (w_2 / w_3)
        * (
            b_4
            / (
                1.0
                * b_3
                * f_2
                * (
                    1
                    - (
                        b_2
                        / (
                            1.0
                            * b_1
                            * f_1
                            * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                            + b_2
                        )
                    )
                    ** (w_2 / w_3)
                )
                + b_4
            )
        )
        ** (w_4 / w_5)
        * (1.0e18 * a_0 * f_0 + b_0)
        / (
            w_1
            * w_3
            * w_5
            * (a_0 * f_0 + 1.0e-18 * b_0) ** 2
            * (
                1.0
                * b_1
                * f_1
                * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                + b_2
            )
            * (
                1.0
                * b_3
                * f_2
                * (
                    1
                    - (
                        b_2
                        / (
                            1.0
                            * b_1
                            * f_1
                            * (1 - (b_0 / (1.0e18 * a_0 * f_0 + b_0)) ** (w_0 / w_1))
                            + b_2
                        )
                    )
                    ** (w_2 / w_3)
                )
                + b_4
            )
        )
        - 1
    )

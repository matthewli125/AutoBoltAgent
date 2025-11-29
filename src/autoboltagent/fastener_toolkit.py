import math
import pandas
import numpy


# Parameters for the Cornwell equation for joints with two plates of the same material as described by Norton for
# equation 15.19 and presented in table 15-8
CORNWELL_PARAMS = pandas.DataFrame(
    numpy.array(
        [
            [0.1, 0.4389, -0.9197, 0.8901, -0.3187],
            [0.2, 0.6118, -1.1715, 1.0875, -0.3806],
            [0.3, 0.6932, -1.2426, 1.1177, -0.3845],
            [0.4, 0.7351, -1.2612, 1.1111, -0.3779],
            [0.5, 0.758, -1.2632, 1.0979, -0.3708],
            [0.6, 0.7709, -1.2600, 1.0851, -0.3647],
            [0.7, 0.7773, -1.2543, 1.0735, -0.3595],
            [0.8, 0.78, -1.2503, 1.0672, -0.3571],
            [0.9, 0.7797, -1.2458, 1.062, -0.3552],
            [1.0, 0.7774, -1.2413, 1.0577, -0.3537],
            [1.25, 0.7667, -1.2333, 1.0548, -0.3535],
            [1.5, 0.7518, -1.2264, 1.0554, -0.3550],
            [1.75, 0.735, -1.2202, 1.0581, -0.3574],
            [2.00, 0.7175, -1.2133, 1.0604, -0.3596],
        ]
    ),
    columns=["j", "p0", "p1", "p2", "p3"],
)


def get_tensile_stress_area(d_major, pitch=None, num_threads=None):
    """
    Returns the tensile stress area of the bolt rounded to 3 decimal places
    :param d_major: Major diameter of the bolt [mm or in]
    :param d_minor: Major diameter of the bolt [mm or in]
    :param pitch: Pitch of the bolt [mm or in]
    :param num_threads: Number of threads per inch [npi]
    :return: the tensile stress area of the bolt [mm^2}
    """

    # Reference eq 15.1 from Norton
    if pitch is not None:
        d_minor = d_major - 1.2268 * pitch
        d_pitch = d_major - 0.649519 * pitch

    else:
        d_pitch = d_major - 0.649519 / num_threads

    return math.pi / 4 * ((d_pitch + d_minor) / 2) ** 2


def get_bolt_shear_area(d_major, pitch=None, num_threads=None, threaded_in_shear=True):
    """
    Calculates the shear area of a bolt depending on whether the shear plane is through threaded or unthreaded region.

    Parameters:
    ----------
    d_major : float
        Major diameter of the bolt [mm or in]
    pitch : float, optional
        Thread pitch [mm or in] (required for metric threads if threaded_in_shear = True)
    num_threads : float, optional
        Number of threads per inch (for imperial threads if threaded_in_shear = True)
    threaded_in_shear : bool
        True if shear plane goes through the threaded portion (default = True)

    Returns:
    -------
    shear_area : float
        Shear area [mm^2 or in^2]
    """

    # Determine the diameter to use based on location of shear plane
    if threaded_in_shear:
        if pitch is not None:
            d_minor = d_major - 1.2268 * pitch
        elif num_threads is not None:
            pitch = 1 / num_threads
            d_minor = d_major - 1.2268 * pitch
        else:
            raise ValueError(
                "Pitch or number of threads must be provided if 'threaded_in_shear' is True."
            )
        d_used = d_minor
    else:
        # Use full major diameter if unthreaded shank is in the shear plane
        d_used = d_major

    # Calculate shear area
    area = (math.pi * d_used**2) / 4

    # # Double the area if in double shear
    # if double_shear:
    #     area *= 2

    return area


def get_bolt_stiffness(a_ts, a_cs, l_unthreaded, l_threaded, E_b):
    """

    :param a_ts: Tensile stress area of the bolt [mm^2 or in^2]
    :param a_cs: Total cross sectional area of the bolt [mm or in]
    :param l_unthreaded: Length of the unthreaded shank within the grip zone[mm or in]
    :param l_threaded: Length of the threaded shank within the grip zone [mm or in]
    :param E_b: Young's modulus of the bolt [MPa or psi]
    :return:The spring constant of the bolt [N/mm or lbf/in]
    """
    return a_ts * a_cs * E_b / (a_cs * l_threaded + a_ts * l_unthreaded)


def get_joint_constant(d_b, l, E_m, E_b):
    """
    Determines the stiffness of clamped members based on the Cornwell method. Makes the assumption that both members
    are of an equivalent material. Reference Eq 15.19 from Norton
    :param d_b: The diameter of the bolt [mm or in]
    :param l: The clamped length of the joint [mm or in]
    :param E_m: The member material Young's modulus [MPa or psi]
    :param E_b: The bolt material Young's modulus [MPa or psi]
    :return: The member stiffness [N/mm or lbf/in]
    """
    j = d_b / l

    # Linearly interpolate through the table to obtain values for p0, p1, p2, and p3

    j_2 = CORNWELL_PARAMS[CORNWELL_PARAMS["j"] >= j - 0.01].iloc[0, 0]

    # Check if j_2 is the max value in the table, if yes, then there is no need to linearly interpolate
    if j_2 > 1.75:
        j_1 = j_2
    else:
        j_1 = CORNWELL_PARAMS[CORNWELL_PARAMS["j"] <= j + 0.01].iloc[-1, 0]

    # Bound the values for the range of J values published
    j_1 = bound_val(j_1, [0.1, 2])
    j_2 = bound_val(j_2, [0.1, 2])

    p_0 = linterp(
        j_1,
        j_2,
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_1]["p0"]),
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_2]["p0"]),
        j,
    )

    p_1 = linterp(
        j_1,
        j_2,
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_1]["p1"]),
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_2]["p1"]),
        j,
    )

    p_2 = linterp(
        j_1,
        j_2,
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_1]["p2"]),
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_2]["p2"]),
        j,
    )

    p_3 = linterp(
        j_1,
        j_2,
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_1]["p3"]),
        float(CORNWELL_PARAMS.loc[CORNWELL_PARAMS["j"] == j_2]["p3"]),
        j,
    )

    # Plate to modulus ratio, r
    r = E_m / E_b

    c = p_3 * r**3 + p_2 * r**2 + p_1 * r + p_0

    return c


def segregate_loads(c, load):
    """
    Identifies the quantity of a load carried by the bolt and by the members
    :param c: Joint stiffness [N/mm or lbf/in]
    :param load: Load applied to the bolt [N or lbf]
    :return: load borne by the bolt, load borne by the members [N or lbf]
    """

    p_b = c * load
    p_m = (1 - c) * load

    return p_b, p_m


def bolt_yield_safety_factor(c, load, preload, a_ts, b_ys):
    """
    Determines the factor of safety against yielding the bolt under statically applied tension load
    :param c: Joint constant [N/mm or lbf/in]
    :param load: Load applied to the joint [N or lbf]
    :param preload: Preload applied to the bolt [N or lbf]
    :param a_ts: Tensile stress area of the bolt [mm^2 or in^2]
    :param b_ys: Yield strength of the bolt [MPa or psi]
    :return:Factor of safety against yielding under statically applied tension load
    """
    # Portion of load carried by the bolt
    f_b = segregate_loads(c, load)[0] + preload

    # Stress in bolt
    sigma_b = f_b / a_ts

    # Factor of safety against yield
    n_y = b_ys / sigma_b

    return n_y


def bound_val(val, limits):
    """
    Bounds a value within limits, setting its value to the upper or lower limit if it is out of bounds
    :param val: The value to be limited
    :param limits: An array of two values, a lower and upper limit
    :return: The bounded value
    """
    if val < limits[0]:
        val = limits[0]
    elif val > limits[1]:
        val = limits[1]

    return val


def linterp(x1, x2, y1, y2, x3):
    """
    Linearly interpolates to determine y3 for a range of values defined by [x1,y1], [x2, y2], [x3, y3 = ?]
    return: y3
    """

    if x2 == x1:
        return y1

    m = (y2 - y1) / (x2 - x1)
    return (x3 - x1) * m + y1

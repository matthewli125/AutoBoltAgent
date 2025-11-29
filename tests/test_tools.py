import autoboltagent.tools


def test_analytical_tool():
    tool = autoboltagent.tools.AnalyticalTool()

    result = tool.forward(
        desired_safety_factor=3.0,
        load=60000,
        preload=0,
        num_bolts=4,
        bolt_diameter=20,
        bolt_elastic_modulus=210,
        plate_elastic_modulus=210,
        bolt_yield_strength=250,
        plate_yield_strength=250,
        plate_thickness=30,
        pitch=1.5,
    )
    print(result)

    assert isinstance(result, str)
    assert (
        "higher than desired" in result
        or "lower than desired" in result
        or "within acceptable range" in result
    )


def test_fea_tool():
    tool = autoboltagent.tools.FiniteElementTool()

    result = tool.forward(
        desired_safety_factor=3.0,
        load=60000,
        preload=0,
        num_bolts=4,
        bolt_diameter=20,
        bolt_elastic_modulus=210,
        plate_elastic_modulus=210,
        bolt_yield_strength=250,
        plate_yield_strength=250,
        plate_thickness=30,
        pitch=1.5,
    )

    print(result)

    assert isinstance(result, str)
    assert (
        "higher than desired" in result
        or "lower than desired" in result
        or "within acceptable range" in result
    )

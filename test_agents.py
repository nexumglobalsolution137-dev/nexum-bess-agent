from agents import forecast_agent, optimization_agent, diagnostic_agent


def test_dispatch_constraints():
    result = optimization_agent(forecast_agent(10, 15), 20, 10, 50)
    assert len(result) == 24
    assert result['SoC (%)'].between(10 - 1e-7, 90 + 1e-7).all()
    assert (result['Charge (kW)'] <= 10 + 1e-7).all()
    assert (result['Discharge (kW)'] <= 10 + 1e-7).all()
    assert (result['Grid Import (kW)'] >= 0).all()
    assert diagnostic_agent(result)

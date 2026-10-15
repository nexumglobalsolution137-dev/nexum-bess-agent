"""Simulation-only BESS agents. No hardware I/O."""
import numpy as np
import pandas as pd


def forecast_agent(solar_kw: float, load_kw: float) -> pd.DataFrame:
    """Create reproducible synthetic hourly profiles (not real forecasts)."""
    hours = np.arange(24)
    solar = solar_kw * np.maximum(0, np.sin(np.pi * (hours - 6) / 12))
    load = load_kw * (0.65 + 0.25 * np.sin(2 * np.pi * (hours - 7) / 24) ** 2)
    tariff = np.where((hours >= 17) & (hours <= 21), 0.35,
                      np.where((hours >= 0) & (hours <= 6), 0.12, 0.20))
    return pd.DataFrame({"Hour": hours, "Solar (kW)": solar,
                         "Load (kW)": load, "Tariff ($/kWh)": tariff})


def optimization_agent(forecast: pd.DataFrame, capacity_kwh: float,
                       power_kw: float, initial_soc: float,
                       min_soc: float = 10, max_soc: float = 90,
                       efficiency: float = 0.95) -> pd.DataFrame:
    """Hourly heuristic: store solar surplus, discharge during peak tariffs.

    Dispatch is energy-constrained, with charge/discharge efficiency applied.
    No export revenue is assumed; unused solar surplus is curtailed.
    """
    energy = capacity_kwh * initial_soc / 100
    rows = []
    for _, r in forecast.iterrows():
        solar, load, tariff = float(r['Solar (kW)']), float(r['Load (kW)']), float(r['Tariff ($/kWh)'])
        surplus = max(0, solar - load)
        deficit = max(0, load - solar)
        charge = min(surplus, power_kw, max(0, (capacity_kwh * max_soc / 100 - energy) / efficiency))
        energy += charge * efficiency
        discharge = 0.0
        if tariff >= 0.30:
            discharge = min(deficit, power_kw, max(0, (energy - capacity_kwh * min_soc / 100) * efficiency))
            energy -= discharge / efficiency
        grid = max(0, deficit - discharge)
        baseline_grid = deficit
        rows.append({**r.to_dict(), 'Charge (kW)': charge, 'Discharge (kW)': discharge,
                     'Grid Import (kW)': grid, 'Baseline Grid (kW)': baseline_grid,
                     'Curtailed Solar (kW)': max(0, surplus - charge),
                     'SoC (%)': 100 * energy / capacity_kwh,
                     'Cost ($)': grid * tariff,
                     'Baseline Cost ($)': baseline_grid * tariff})
    return pd.DataFrame(rows)


def diagnostic_agent(dispatch: pd.DataFrame, min_soc: float = 10,
                     max_soc: float = 90) -> list[str]:
    warnings = []
    if (dispatch['SoC (%)'] < min_soc - 1e-6).any() or (dispatch['SoC (%)'] > max_soc + 1e-6).any():
        warnings.append('ALERT: Simulated state of charge exceeded configured bounds.')
    if dispatch['Curtailed Solar (kW)'].sum() > 0.1:
        warnings.append('Solar surplus is curtailed when the battery cannot absorb it.')
    if dispatch['Grid Import (kW)'].max() > 10:
        warnings.append('Peak grid import exceeds 10 kW; review site demand limits.')
    if not warnings:
        warnings.append('No threshold violations detected in this simplified simulation.')
    return warnings


def supervisor_agent(dispatch: pd.DataFrame, warnings: list[str]) -> str:
    baseline = dispatch['Baseline Cost ($)'].sum()
    cost = dispatch['Cost ($)'].sum()
    savings = baseline - cost
    return (f"### AI Supervisor — simulated dispatch summary\n"
            f"- Battery charges from excess solar and discharges during the synthetic peak-price window (17:00–21:00).\n"
            f"- Grid import: **{dispatch['Grid Import (kW)'].sum():.1f} kWh** over 24 hours.\n"
            f"- Estimated grid energy cost: **${cost:.2f}** vs **${baseline:.2f}** without storage.\n"
            f"- Estimated daily savings: **${savings:.2f}** (illustrative tariffs, excludes battery degradation and capital costs).\n"
            f"- End-of-day SoC: **{dispatch['SoC (%)'].iloc[-1]:.1f}%**.\n\n"
            f"**Diagnostic observations**\n" + '\n'.join(f'- {w}' for w in warnings))

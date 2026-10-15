"""Nexum Global Solution BESS AI Operations Agent — simulation demo."""
import gradio as gr
import plotly.graph_objects as go
from agents import forecast_agent, optimization_agent, diagnostic_agent, supervisor_agent


def run_simulation(solar_kw, load_kw, battery_kw, battery_kwh, initial_soc):
    forecast = forecast_agent(float(solar_kw), float(load_kw))
    dispatch = optimization_agent(forecast, float(battery_kwh), float(battery_kw), float(initial_soc))
    warnings = diagnostic_agent(dispatch)
    summary = supervisor_agent(dispatch, warnings)
    flow = go.Figure()
    for col in ['Solar (kW)', 'Load (kW)', 'Charge (kW)', 'Discharge (kW)', 'Grid Import (kW)']:
        flow.add_trace(go.Scatter(x=dispatch['Hour'], y=dispatch[col], mode='lines+markers', name=col))
    flow.update_layout(title='Digital Twin — Hourly Power Flows', xaxis_title='Hour',
                       yaxis_title='Power (kW)', template='plotly_white', legend=dict(orientation='h'))
    soc = go.Figure()
    soc.add_trace(go.Scatter(x=dispatch['Hour'], y=dispatch['SoC (%)'], mode='lines+markers', name='SoC'))
    soc.update_layout(title='Battery State of Charge', xaxis_title='Hour',
                      yaxis_title='SoC (%)', yaxis_range=[0, 100], template='plotly_white')
    shown = dispatch.round(2)
    return summary, flow, soc, shown


with gr.Blocks(title='Nexum BESS AI Operations Agent') as demo:
    gr.Markdown('# 🔋 Nexum Global Solution — BESS AI Operations Agent')
    gr.Markdown('**Simulation-only prototype** | Solar + Industrial Load + Grid + Battery | Forecast → Optimize → Diagnose → Explain')
    with gr.Row():
        solar = gr.Slider(1, 50, value=10, step=1, label='Solar PV capacity (kW)')
        load = gr.Slider(3, 50, value=15, step=1, label='Industrial peak load setting (kW)')
    with gr.Row():
        power = gr.Slider(1, 50, value=10, step=1, label='BESS power (kW)')
        capacity = gr.Slider(5, 200, value=20, step=5, label='BESS energy (kWh)')
        soc = gr.Slider(10, 90, value=50, step=5, label='Initial SoC (%)')
    run = gr.Button('Run BESS Agents', variant='primary')
    report = gr.Markdown()
    with gr.Row():
        flow_plot = gr.Plot(label='Power Flow')
        soc_plot = gr.Plot(label='Battery SoC')
    table = gr.Dataframe(label='24-hour Simulation Data', interactive=False)
    gr.Markdown('⚠️ **Not for physical BESS control.** Synthetic profiles, illustrative prices and simplified dispatch; no BMS/PCS commands, live telemetry, or certified safety logic.')
    run.click(run_simulation, inputs=[solar, load, power, capacity, soc],
              outputs=[report, flow_plot, soc_plot, table])
    demo.load(run_simulation, inputs=[solar, load, power, capacity, soc],
              outputs=[report, flow_plot, soc_plot, table])

if __name__ == '__main__':
    demo.launch()

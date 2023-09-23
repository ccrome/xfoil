import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import airfoil_converter.airfoil
import importlib
from pathlib import Path
import zipfile
import io

# Initialize the Flask app
app = dash.Dash(__name__)

airfoil_dir = "airfoils/airfoils-interpolated"

# Sample local file names (replace with your actual file names)

resources = importlib.resources.files('airfoil_converter').joinpath("airfoils").joinpath("airfoils-interpolated")

file_names = []
file_paths = []
for f in  resources.iterdir():
    file_paths.append(f)
file_paths = file_paths

file_paths = sorted(file_paths)
file_names = [Path(f.name).stem for f in file_paths]


# Define the layout of the app
app.layout = html.Div([
    html.H1("Airfoil to DXF and SVG converter and viewer for xfoil"),
    dcc.Dropdown(
        id='file-dropdown',
        options=[{'label': file, 'value': str(path)} for path, file in zip(file_paths, file_names)],
        value=None,
        multi=True,
        placeholder="Select a file",
    ),
    dcc.Graph(id='plot'),
    html.Div(
        [
            html.Label("Enter the size for downloaded files"),
            dcc.Input(
                id='size-id',
                type='number',
                value=100,
                step=1),
        ]),

    html.Div([
        html.Button('Download SVG', id='btn-download-svg'),
        dcc.Download(id="download-svg"),
    ]),
    html.Div([
        html.Button('Download DXF', id='btn-download-dxf'),
        dcc.Download(id="download-dxf"),
    ]),
])

@app.callback(
    Output("download-svg", "data"),
    Input("btn-download-svg", "n_clicks"),
    State('file-dropdown', 'value'),
    prevent_initial_call=True
)
def svg_download(n_clicks, file_list):
    def write_archive(bytes_io):
        with zipfile.ZipFile(bytes_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in file_list:
                a = airfoil_converter.airfoil.Airfoil(filename=f)
                svg_buffer = io.StringIO()
                f = Path(f)
                fname = str(f.name) + ".svg"
                a.write_svg(svg_buffer)
                svg_buffer.seek(0)
                zipf.writestr(fname, svg_buffer.getvalue())
                svg_buffer.close()
            
    return dcc.send_bytes(write_archive, "airfoils_svg.zip")

@app.callback(
    Output("download-dxf", "data"),
    Input("btn-download-dxf", "n_clicks"),
    State('file-dropdown', 'value'),
    prevent_initial_call=True
)
def dxf_download(n_clicks, file_list):
    def write_archive(bytes_io):
        with zipfile.ZipFile(bytes_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in file_list:
                a = airfoil_converter.airfoil.Airfoil(filename=f)
                dxf_buffer = io.StringIO()
                f = Path(f)
                fname = str(f.name) + ".dxf"
                a.write_dxf(dxf_buffer)
                dxf_buffer.seek(0)
                zipf.writestr(fname, dxf_buffer.getvalue())
                dxf_buffer.close()
    return dcc.send_bytes(write_archive, "airfoils_dxf.zip")


@app.callback(
    Output('plot', 'figure'),
    [Input('file-dropdown', 'value')],
)
def update_plot(selected_files):
    layout = go.Layout(
        title='Scatter Plot with Two Traces and Legend',
        xaxis=dict(title='X-Axis'),
        yaxis=dict(title='Y-Axis'),
    )
    fig = go.Figure(layout=layout)
    fig.update_xaxes(range=[-0.05, 1.05])
    if selected_files is None:
        # If no file is selected, return an empty figure
        pass
    else:
        for selected_file in selected_files:
            # Read the selected file (assuming it's a CSV file)
            af = airfoil_converter.airfoil.Airfoil(filename=selected_file)

            # Create a scatter plot (you can customize this part based on your data)
            name = Path(Path(selected_file).name).stem
            coords = af.get_coords(closed=True)
            trace = go.Scatter(x=coords[:, 0], y=coords[:, 1], name=name, showlegend=True)
            fig.add_trace(trace)
    return fig

def main(debug=True):
    app.run_server(debug=debug, host="0.0.0.0")
    
if __name__ == '__main__':
    main()

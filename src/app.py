import dash
from dash import html, dcc, dash_table, Input, Output
import plotly.express as px
import pandas as pd

# Create dash app
app = dash.Dash(
    __name__,
    title="A4_MCM7183_MuhdAfeef",
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/maplibre-gl@2.1.8/dist/maplibre-gl.css"
    ],
)
server = app.server

# Import main data
df = pd.read_csv("src/input/data_cleaned.csv")

# Import lat/long data
lat_long_df = pd.read_csv("src/input/lat_long_data.csv")

# Merge data on city
df = df.merge(lat_long_df, on="city", how="left")

# Create layout
app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.Div(
            children="Afeef's Weather Dashboard of Places in Malaysia",
            style={"fontSize": 24},
        ),
        dash_table.DataTable(data=df.to_dict("records"), page_size=10),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Temperature Graph",
                    children=[
                        dcc.RangeSlider(
                            id="hour-range-slider",
                            min=df["hour"].min(),
                            max=df["hour"].max(),
                            value=[df["hour"].min(), df["hour"].max()],
                            marks={
                                str(hour): str(hour) for hour in df["hour"].unique()
                            },
                            step=1,
                            tooltip={"always_visible": True, "placement": "bottom"},
                        ),
                        dcc.Graph(id="temperature-graph"),
                    ],
                ),
                dcc.Tab(
                    label="Humidity Graph",
                    children=[
                        dcc.Dropdown(
                            id="state-dropdown",
                            options=[{"label": "All States", "value": "All"}]
                            + [
                                {"label": state, "value": state}
                                for state in df["state"].unique()
                            ],
                            value="All",
                            clearable=False,
                            style={"width": "50%"},
                        ),
                        dcc.Graph(id="humidity-graph"),
                    ],
                ),
                dcc.Tab(
                    label="Pressure Histogram",
                    children=[
                        dcc.Graph(
                            figure=px.histogram(
                                df,
                                x="state",
                                y="pressure",
                                histfunc="avg",
                                title="Average Pressure (hPa) of States in Malaysia",
                            )
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Geographical Plot",
                    children=[
                        dcc.Slider(
                            id="hour-slider",
                            min=df["hour"].min(),
                            max=df["hour"].max(),
                            value=df["hour"].min(),
                            marks={
                                str(hour): str(hour) for hour in df["hour"].unique()
                            },
                            step=1,
                            tooltip={"always_visible": True, "placement": "bottom"},
                        ),
                        dcc.Graph(id="geo-plot"),
                    ],
                ),
            ]
        ),
        html.Div(
            id="summary-text",
            style={"margin-top": "20px", "fontSize": 16},
            children=[
                "This dashboard provides insights into weather patterns across various locations in Malaysia. ",
                "You can explore temperature variations over time, humidity levels, and pressure statistics, ",
                "as well as visualize geographical temperature distributions at specific hours. ",
                "Created by Muhammad Afeef Bin Mazlan, 241PM58017 for MCM7183 Assignment 4 - August 2024.",
            ],
        ),
    ],
)


@app.callback(
    Output("temperature-graph", "figure"), Input("hour-range-slider", "value")
)
def update_graph(selected_range):
    filtered_df = df[
        (df["hour"] >= selected_range[0]) & (df["hour"] <= selected_range[1])
    ]
    fig = px.line(
        filtered_df,
        x="hour",
        y="temperature",
        color="city",
        title=f"Temperature by Hour in Cities of Malaysia (Hours: {selected_range[0]} to {selected_range[1]})",
    )
    return fig


@app.callback(Output("humidity-graph", "figure"), Input("state-dropdown", "value"))
def update_humidity_graph(selected_state):
    if selected_state == "All":
        filtered_df = df
    else:
        filtered_df = df[df["state"] == selected_state]

    fig = px.scatter(
        filtered_df,
        x="temperature",
        y="humidity",
        color="city",
        title=f"Temperature vs Humidity in {selected_state} (if not All States)",
    )
    return fig


@app.callback(
    Output("geo-plot", "figure"),
    Input("state-dropdown", "value"),
    Input("hour-slider", "value"),  # Add hour slider as input
)
def update_geo_plot(selected_state, selected_hour):
    if selected_state == "All":
        filtered_df = df[df["hour"] == selected_hour]
    else:
        filtered_df = df[
            (df["state"] == selected_state) & (df["hour"] == selected_hour)
        ]

    fig = px.scatter_map(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="temperature",
        hover_name="city",
        title=f"Geographical Distribution of Temperature at Hour {selected_hour} in {selected_state} (if not All States)",
        color_continuous_scale=px.colors.sequential.Plasma,
        zoom=4,  # Adjust zoom level as necessary
        map_style="carto-positron",  # Use OpenStreetMap style
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

import plotly
import plotly.graph_objs as go
import plotly.io as pct

import pandas as pd
import numpy as np
import json


def create_plot():
    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe

    fig = go.Figure(go.Bar(
            x=df['x'],
            y=df['y']))

    graphJSON = pct.to_json(fig)

    return graphJSON


def create_heatmap():

    layout = go.Layout(
        xaxis=go.layout.XAxis(
            showticklabels=False),
        yaxis=go.layout.YAxis(
            showticklabels=False
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    fig = go.Figure(data=go.Heatmap(
        z=[[1, 10, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20], [1, 10, 30, 50, 1], [30, 60, 1, -10, 20], [20, 1, 60, 80, 30]],
        x=['1', '2', '3', '4', '5'],
        y=['1', '2', '3', '4', '5', '6'],
        hoverongaps=False), layout=layout)

    fig.update_traces(showscale=False)

    graphJSON = pct.to_json(fig)

    return graphJSON
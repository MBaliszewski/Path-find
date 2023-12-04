from dash import Dash, html, dcc, Input, Output, callback, State, ctx
import plotly.graph_objects as go
import numpy as np
import json
from read_roads import make_graph, astar, dijkstra, xy_from_path

#############
workspace = 'dane\\torun'
layer = 'L4_1_BDOT10k__OT_SKJZ_L.shp'
algorithm = 'astar'
type = 'fastest'
alternative_path = True
#############

graph = make_graph(workspace, layer)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

all_data = []
colors = ['rgba(0, 13, 255, 0.92)', 'rgba(0, 13, 255, 0.52)']
names = ['Path', 'Alternative path']

fig = go.Figure(go.Scattermapbox(
    lat=[node.x_4326 for node in graph.nodes.values()],
    lon=[node.y_4326 for node in graph.nodes.values()],
    mode='markers',
    showlegend=True,
    name='Nodes',
    hoverinfo='none',
    marker=go.scattermapbox.Marker(
            size=5,
            color='rgb(255, 0, 0)',
    ),
))

fig.update_layout(
    mapbox = dict(style='open-street-map',
                  center=dict(lat=np.median(fig.data[0].lat),
                              lon=np.median(fig.data[0].lon)),
                  zoom=12),
    clickmode='event+select',
    uirevision='some-constant',
)

app.layout = html.Div([
    dcc.Graph(id='map',
              figure=fig,
              style={'width': '100%', 'height': '100vh'}),

    html.Button('CLEAR', id='clear-btn',
                style={'width': '80%', 'marginLeft': '8%', 'marginRight': '12%'}),

    dcc.ConfirmDialog(
        id='alert',
        message='No path found between selected points.',
        displayed=False,
    ),
])


@app.callback(
    Output('map', 'figure'),
    Output('alert', 'displayed'),
    Input('map', 'selectedData'),
    Input('clear-btn', 'n_clicks'))
def display_click_data(clickData, n_clicks):
    triggered = ctx.triggered_id

    if triggered == 'clear-btn':
        fig.data = [fig.data[0]]
        all_data.clear()
        return fig, False
    if triggered == 'map':
        if clickData is not None:
            lat = clickData['points'][0]['lat']
            lon = clickData['points'][0]['lon']
            
            fig.add_trace(go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode='markers',
                showlegend=False,
                name='',
                hoverinfo='none',
                marker=go.scattermapbox.Marker(
                    size=10,
                    color='rgb(0, 0, 204)',
                ),
            ))
            
            all_data.append(clickData)
            if len(all_data) == 2:
                node_start_id = all_data[0]['points'][0]['pointIndex']
                node_end_id = all_data[1]['points'][0]['pointIndex']
                graph.start_node = graph.nodes[node_start_id + 1]
                graph.end_node = graph.nodes[node_end_id + 1]

                if algorithm == 'astar':
                    paths, _ = astar(graph, type, alternative_path)
                elif algorithm == 'dijkstra':
                    paths, _ = dijkstra(graph, type, alternative_path)
 
                if paths is None:
                    return fig, True
                else:
                    for idx, path in enumerate(paths):
                        lats, lons = xy_from_path(path)
                        fig.add_trace(go.Scattermapbox(
                            lat=lats,
                            lon=lons,
                            mode='lines',   
                            showlegend=True,
                            name=names[idx],
                            hoverinfo='none',
                            line=dict(width=5, color=colors[idx])
                        ))

                        fig.add_trace(go.Scattermapbox(
                            lat=[lats[0]],
                            lon=[lons[0]],
                            mode='markers',
                            showlegend=False,
                            name='',
                            hovertemplate='START',
                            marker=go.scattermapbox.Marker(
                                size=16,
                                color='rgb(0, 0, 204)',
                            ),
                        ))

                        fig.add_trace(go.Scattermapbox(
                            lat=[lats[-1]],
                            lon=[lons[-1]],
                            mode='markers',
                            showlegend=False,
                            name='',
                            hovertemplate='STOP',
                            marker=go.scattermapbox.Marker(
                                size=16,
                                color='rgb(0, 0, 204)',
                            ),
                        ))
                        
            return fig, False    
    return fig, False

if __name__ == '__main__':
    app.run(debug=True)
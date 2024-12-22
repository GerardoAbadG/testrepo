# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart for launch success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, 
        max=max_payload, 
        step=1000,
        marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
        value=[min_payload, max_payload]
    ),

    # Scatter plot for payload vs success outcome
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart based on launch site selection
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Use all data for the pie chart
        fig = px.pie(
            data_frame=spacex_df,
            names='Launch Site',
            title='Total Success Launches By Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']

        # Create a pie chart for the selected site
        fig = px.pie(
            data_frame=success_counts,
            values='count',
            names='class',
            title=f'Total Success vs Failure Launches for site {selected_site}'
        )
    return fig

# Callback for scatter chart based on launch site and payload range selection
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Launch Sites',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {selected_site}',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()

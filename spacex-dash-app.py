# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                  dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    if entered_site == 'ALL':
        success_by_site = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        
        fig = px.pie(values=success_by_site.values, 
                     names=success_by_site.index, 
                     title='Successful Launches by Site')
        return fig
    else:
        success_count = filtered_df['class'].sum()
        failure_count = len(filtered_df) - success_count  
        
        fig = px.pie(values=[success_count, failure_count], 
                     names=['Success', 'Failure'], 
                     title=f'Success vs Failure Counts for {entered_site}')
        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(selected_site, payload_range):
    if payload_range is None:
        low_filter = 0
        high_filter = 10000
    else:
        low_filter = payload_range[0]
        high_filter = payload_range[1]
    
    # Filter dataframe based on payload range first
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low_filter) & 
                           (spacex_df['Payload Mass (kg)'] <= high_filter)]
    
    # If-Else statement to check if ALL sites were selected or just a specific launch site
    if selected_site == 'ALL':
        # If ALL sites are selected, render scatter plot with all values
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class',
                         color="Booster Version Category",
                         title='Correlation between Payload Mass and Mission Outcome for All Sites',
                         labels={'class': 'Mission Outcome', 
                                 'Payload Mass (kg)': 'Payload Mass (kg)',
                                 'Booster Version Category': 'Booster Version'},
                         hover_data=['Launch Site'])
    else:
        # If a specific launch site is selected, filter the dataframe
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        # Render scatter chart for the selected site
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class',
                         color="Booster Version Category",
                         title=f'Correlation between Payload Mass and Mission Outcome for {selected_site}',
                         labels={'class': 'Mission Outcome', 
                                 'Payload Mass (kg)': 'Payload Mass (kg)',
                                 'Booster Version Category': 'Booster Version'},
                         hover_data=['Launch Site'])
    
    # Customize y-axis to show 0 and 1 with labels for better readability
    fig.update_yaxes(tickvals=[0, 1], ticktext=['Failure', 'Success'])
    
    return fig
# Run the app
if __name__ == '__main__':
    app.run()

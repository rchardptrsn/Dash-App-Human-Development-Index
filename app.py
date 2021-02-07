# First Dash App

# Import libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.figure_factory as ff

import pandas as pd 
import numpy as np
from sklearn.preprocessing import StandardScaler

# Read the data from CSV
# query = 'SELECT * FROM DevIndex WHERE level="Subnat";'


df = pd.read_csv('data.csv')

df = df.query('level == "Subnat"')

# Find unique countries
countries = df['country'].unique()

# Rename columns
df = df.rename(columns={'shdi':'Sub-National Human Development Index','healthindex':'Health Index',
        'incindex':'Income Index','edindex':'Educational Index','lifexp':'Life Expectancy','lgnic':'Log Gross National Income Per Capita',
        'esch':'Expected Years Schooling','msch':'Mean Years Schooling','pop':'Population (thousands)'})

# Create a list of columns for filtering later
columns = df.columns[6:]


# Dash App


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Beanstalk looks for application by default, 
# if this isn't set you will get a WSGI error.
application = app.server

markdown_text = '''
# Human Development Index
## A Subnational Perspective
### Data collected by the [United Nations Human Development Report](http://www.hdr.undp.org/)
### Subnational Data provided by [Global Data Lab](https://globaldatalab.org/shdi/)
### The chart below shows regional data for the selected country from 1990 to 2017
'''




app.layout = html.Div([
    dcc.Markdown(children=markdown_text),

    # Select a country

    html.Div([
        html.P("Please select a country:")
    ]),
    
    html.Div([
        dcc.Dropdown(
            id='country-selector',
            options=[{'label':i,'value':i} for i in countries],
            value='Uganda'
        )
    ]),

    # Select an X axis Variable

    html.Div([
        html.P("  "),
        html.P("Please select two variables for comparison:")
    ]),
    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label':i,'value':i} for i in columns],
            value='Health Index'
        )
    ],
    style={'width':'48%','display':'inline-block'}),

    # Select a Y axis variable

    html.Div([
        dcc.Dropdown(
            id='yaxis-column',
            options=[{'label':i,'value':i} for i in columns],
            value='Income Index'
        )
    ],
    style={'width':'48%','display':'inline-block'}),

    # Graph
    dcc.Graph(id='scatterplot'),

    # Distplot
    dcc.Markdown(children='''## Distribution Plot of the Selected Variables'''),
    dcc.Graph(id='distplot'),
    
    html.Div([
        html.P("  "),
        html.P("Last updated: January 19, 2020."),
        html.P("  ")
    ])



])

# Callbacks

# Scatterplot callback
@app.callback(
    Output('scatterplot','figure'),
    [Input('country-selector','value'),
    Input('xaxis-column','value'),
    Input('yaxis-column','value')])

def update_scatterplot(country_selector,xaxis_column,yaxis_column):

    # Filter by the country selector box
    filtered_df = df[df['country'] == country_selector]
    traces = []
    for i in filtered_df.region.unique():
        df_region = filtered_df[filtered_df['region'] == i]
        traces.append(dict(
            x = df_region[xaxis_column],
            y = df_region[yaxis_column],
            text = df_region['year'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i  
        ))


    return {
        'data': traces,
        'layout':dict(
            xaxis={
                'title':xaxis_column 
            },
            yaxis={
                'title':yaxis_column    
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

# distplot callback
@app.callback(
    Output('distplot','figure'),
    [Input('country-selector','value'),
    Input('xaxis-column','value'),
    Input('yaxis-column','value')])

def update_distplot(country_selector,xaxis_column,yaxis_column):

    # Specify group labels for later
    group_labels = [xaxis_column,yaxis_column]

    # Filter by the country selector box
    distplot_country = df[df['country'] == country_selector].dropna()
    # Grab the two columns we are interested in
    distplot_df = distplot_country.loc[:,group_labels]

    # Apply sklearn standardscaler
    scaler = StandardScaler()
    std_distplot_df = scaler.fit_transform(distplot_df)

    # Reduce the filtered dataframe to 2 numpy arrays
    array1 = np.double(std_distplot_df[:,0])
    array2 = np.double(std_distplot_df[:,1])

    data = [array1, array2]
    # Figure Factory (ff) returns both data and layout
    return ff.create_distplot(data,group_labels, bin_size=.2)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port=80) #debug=True,
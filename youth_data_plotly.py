import pandas as pd
import plotly.express as px

# Import CSV and create initial DFs
all_youth = pd.read_csv("20230705_youth.csv")
youth = all_youth[all_youth['Employment Status'] == 'Active'].copy()
active_youth = youth['Employment Status'].count()
total_youth = all_youth['Employee Number'].nunique()
df1 = all_youth[all_youth['Reason for Leaving'] == "Found a Job"]
found_a_job = df1['Employee Number'].nunique()
number_of_sites = youth['Site Placement'].nunique()
# Count the number of youth per area
area_counts = youth['Area'].value_counts().reset_index()
area_counts.columns = ['Area', 'Count']
fig_area = px.bar(area_counts, x='Area', y='Count', color="Area", labels={'Count':'Number of Youths', 'Area': ''}, title='Breakdown by Area')

# Count the number of youth per school
school_counts = youth['Site Placement'].value_counts().reset_index()
school_counts.columns = ['Site Placement', 'Count']
fig_school = px.bar(school_counts, x='Site Placement', y='Count', color="Site Placement", labels={'Count':'Number of Youths', 'School/ECDC': ''}, title='Breakdown by School/ECDC')

# Count the number of youth per race
race_counts = youth['Race'].value_counts().reset_index()
race_counts.columns = ['Race', 'Count']
fig_race = px.pie(race_counts, values='Count', names='Race', title='Breakdown by Race')

# Count the number of youth per gender
gender_counts = youth['Gender'].value_counts().reset_index()
gender_counts.columns = ['Gender', 'Count']
fig_gender = px.pie(gender_counts, values='Count', names='Gender', title='Breakdown by Gender')

# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([

    html.H1("Youth Dashboard"),
    html.Br(),
    html.Br(),
    html.H2(f"Number of Youth Currently Employed: {str(active_youth)}"),
    html.Br(),
    html.H2(f"Number of Youth Employed Past 2.5 Years: {str(total_youth)}"),
    html.Br(),
    html.H2(f"Number of Youth Who Have Found Further Employment: {str(found_a_job)}"),
    html.Br(),
    html.H2("Youth per Site"),
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': i, 'value': i} for i in youth['Site Placement'].unique()],
        value='Charles Duna P School'
    ),
    dcc.Graph(id='site-bar-chart'),
    html.Br(),
    html.H2("Youth per Mentor"),
    dcc.Dropdown(
        id='mentor-dropdown',
        options=[{'label': i, 'value': i} for i in youth['Mentor'].unique()],
        value="Nosisa Ncobo"
    ),
    dcc.Graph(id='mentor-bar-chart'),
    html.Br(),
    html.H2("Youth by Area"),
    dcc.Graph(id='area-bar-chart', figure=fig_area),
    html.Br(),
    html.H2("Youth by School"),
    html.H4(f"Number of Sites: {str(number_of_sites)}"),
    dcc.Graph(id='school-bar-chart', figure=fig_school),
    html.H2("Youth by Gender"),
    dcc.Graph(id='gender-bar-chart', figure=fig_gender),
    html.Br(),
    html.H2("Youth by Race"),
    dcc.Graph(id='race-bar-chart', figure=fig_race),
    html.Br(),
])

# Define callback
@app.callback(
    [Output('site-bar-chart', 'figure'),
     Output('mentor-bar-chart', 'figure')],
    [Input('site-dropdown', 'value'),
     Input('mentor-dropdown', 'value')]
)
def update_graph(selected_site, selected_mentor):
    # First chart based on Site Placement
    filtered_df_site = youth[youth['Site Placement'] == selected_site]
    fig1 = px.histogram(filtered_df_site, x='Job Title', color='Job Title',
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    fig1.update_layout(showlegend=False)

    # Second chart based on Mentor
    filtered_df_mentor = youth[youth['Mentor'] == selected_mentor]
    fig2 = px.histogram(filtered_df_mentor, x='Job Title', color='Job Title',
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    fig2.update_layout(showlegend=False)

    return fig1, fig2

# Run app
if __name__ == '__main__':
    app.run_server(port=8053)

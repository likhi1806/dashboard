# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output,dash_table
import plotly.express as px
import pandas as pd

df=pd.read_csv('visitor_data_native.csv',delimiter='|',low_memory=False)
updated_cols=['ts_date', 'hour', 'conversion_status','raw_publisher_id','enriched_country', 'enriched_derived_device', 'enriched_derived_os','enriched_publisher_domain', 'ad_adgroup_id', 'ad_advertiser_id','ad_campaign_id', 'ad_keyword','click_browser', 'click_state','click_city', 'click_click_status', 'conv_weight', 'conv_value', 'top_level_category_name','seller_tag_id', 'integration_type', 'visitor_id']
new_df=df[updated_cols].sort_values(by=['ts_date','hour'])



def generate_table(dataframe, max_rows=1000):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app = Dash(__name__)

app.layout = html.Div([

    html.Div(children=[
        
    html.Label('Visitor ID'),
    dcc.Input(id='visitor_id',value='', type='text'),

    html.Br(),
       
    ], style={'padding': 10,}),

    html.Div(children=[
        
    html.Label('Start Date'),
    dcc.Input(id='start_date', type='number'),

    html.Br(),
       
    ], style={'padding': 10,}),

    html.Div(children=[
        
    html.Label('End Date'),
    dcc.Input(id='end_date', type='number'),

    html.Br(),
       
    ], style={'padding': 10,}),

    html.H4(children='Visitor Data'),

    html.Div(id='div-1'),

    #dash_table.DataTable(new_df.to_dict('records'), [{"name": i, "id": i} for i in new_df.columns])

    dcc.Graph(id='conv_status'),
    dcc.Graph(id='graph')  

    
    
],style={'display': 'flex', 'flex-direction': 'column'})

@app.callback(
    Output('graph','figure'),
    Output('conv_status', 'figure'),
    Output('div-1', 'children'),
    Input('visitor_id', 'value'),
    Input('start_date', 'value'),
    Input('end_date', 'value'))
def update_graph(visitor_id,start_date,end_date):
    dff = new_df[new_df['visitor_id']==visitor_id]
    dff_1 =dff[dff['ts_date']>=start_date]
    dff_2=dff_1[dff_1['ts_date']<=end_date]
    #final_df=dff.query('ts_date>=start_date & ts_date<=end_date')

    
    new_dff_1 =new_df[new_df['ts_date']>=start_date]
    new_dff_2=new_dff_1[new_dff_1['ts_date']<=end_date]

    df_grouped_conv = dff_2.groupby(['conversion_status'])['conversion_status'].count()
    dff_grouped_conv=pd.DataFrame({'conversion_status':df_grouped_conv.index, 'count':df_grouped_conv.values})

    fig_conv= px.pie(dff_grouped_conv, names='conversion_status', values='count',title='Conversion Status in the given period')


    df_grouped = new_dff_2.groupby(['enriched_country'])['enriched_country'].count()
    dff_3=pd.DataFrame({'enriched_country':df_grouped.index, 'count':df_grouped.values})

    fig = px.pie(dff_3, values='count', names='enriched_country', title='Population of European continent')
    return fig,fig_conv,dash_table.DataTable(dff_2.to_dict('records'), [{"name": i, "id": i} for i in dff_2.columns])



if __name__ == '__main__':
    app.run_server(debug=True)

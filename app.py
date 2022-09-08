# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output,dash_table
import plotly.express as px
import pandas as pd
import numpy as np

df=pd.read_csv('visitor_data_native.csv',delimiter='|',low_memory=False)
updated_cols=['ts_date', 'hour', 'conversion_status','raw_publisher_id','enriched_country', 'enriched_derived_device', 'enriched_derived_os','enriched_publisher_domain', 'ad_adgroup_id', 'ad_advertiser_id','ad_campaign_id', 'ad_keyword','click_browser', 'click_state','click_city', 'click_click_status', 'conv_weight', 'conv_value', 'top_level_category_name','seller_tag_id', 'integration_type', 'visitor_id']
categorical_values=['conversion_status','raw_publisher_id','enriched_country', 'enriched_derived_device', 'enriched_derived_os','enriched_publisher_domain', 'ad_adgroup_id', 'ad_advertiser_id','ad_campaign_id', 'ad_keyword','click_browser', 'click_state','click_city', 'click_click_status','top_level_category_name','seller_tag_id', 'integration_type']
new_df=df[updated_cols].sort_values(by=['ts_date','hour'])
new_df[['in_date']] = new_df[['ts_date']].applymap(str).applymap(lambda s: "{}/{}/{}".format(s[4:6],s[6:], s[0:4]))
new_df[['time']]=new_df[['hour']].applymap(str)
new_df['time_str']=new_df['time'].str.zfill(2)
new_df['in_date']=new_df['in_date'].apply(lambda s:s+"T")
new_df['date_time']=new_df['in_date']+new_df['time_str']
 

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

    
    html.Label('Columns required'),
    dcc.Dropdown(categorical_values,
                 placeholder="Select columns", 
                 multi=True,
                 id='req_attr'
    ),
    
    html.Br(),


    html.Div(
        [   
            html.Div([
                html.Label('Top_level_category_name',id='dynamic-dropdown-container1'),
                ],
            style={
                'display':'block'
                }   
            ),

            html.Div([
                dcc.Dropdown(
                    id='top_level_category_name_label',
                    options=[i for i in new_df.top_level_category_name.unique()],
                    multi=True
            )],
            style={
                'display':'block'
                }   
            ),

            html.Div([
                html.Label('Browser',id='dynamic-dropdown-container2'),
                ],
            style={
                'display':'block'
                }   
            ),


            html.Div([
                dcc.Dropdown(
                    id='click_browser_label',
                    options=[i for i in new_df.click_browser.unique()],
                    multi=True
                )],
                style={
                    'display':'block'
                }    
            ),

            html.Div([
                html.Label('Enriched_country',id='dynamic-dropdown-container3'),
                ],
            style={
                'display':'block'
                }   
            ),

            html.Div([
                dcc.Dropdown(
                    id='enriched_country_label',
                    options=[i for i in df.enriched_country.unique()],
                    multi=True
            )],
            style={
                'display':'block'
                }   
            ),
        ],
    ),

    




    html.H4(children='Visitor Timeline'),

    dcc.Graph(id='timeline_graph'),

    #html.Div(id='div-1'),

    #dash_table.DataTable(new_df.to_dict('records'), [{"name": i, "id": i} for i in new_df.columns])

    dcc.Graph(id='conv_status'),
    dcc.Graph(id='graph')  

    
    
],style={'display': 'flex', 'flex-direction': 'column'})



@app.callback(
    Output('dynamic-dropdown-container1','style'),
    Output('top_level_category_name_label','style'),
    Input('req_attr','value')
)
def category_dropdown(req_attr):
    if req_attr is not None and 'top_level_category_name' in req_attr:
        return {'display': 'block'},{'display': 'block'}
    else:
        return {'display': 'none'},{'display': 'none'}


@app.callback(
    Output('dynamic-dropdown-container2','style'),
    Output('click_browser_label','style'),
    Input('req_attr','value')
)
def category_dropdown(req_attr):
    if req_attr is not None and 'click_browser' in req_attr:
        return {'display': 'block'},{'display': 'block'}
    else:
        return {'display': 'none'},{'display': 'none'}


@app.callback(
    Output('dynamic-dropdown-container3','style'),
    Output('enriched_country_label','style'),
    Input('req_attr','value')
)
def category_dropdown(req_attr):
    if req_attr is not None and 'enriched_country' in req_attr:
        return {'display': 'block'},{'display': 'block'}
    else:
        return {'display': 'none'},{'display': 'none'}



@app.callback(

    Output('timeline_graph','figure'),
    Output('graph','figure'),
    Output('conv_status', 'figure'),
    #Output('div-1', 'children'),
    Input('visitor_id', 'value'),
    Input('start_date', 'value'),
    Input('end_date', 'value'),
    Input('req_attr','value'),
    Input('top_level_category_name_label','value'),
    Input('click_browser_label','value'),
    Input('enriched_country_label','value'),

    )
def dashboard(visitor_id,start_date,end_date,req_attr,top_level_category_name_label,click_browser_label,enriched_country_label):
    dff = new_df[new_df['visitor_id']==visitor_id]
    dff_1 =dff[dff['ts_date']>=start_date]
    dff_2=dff_1[dff_1['ts_date']<=end_date]

   # dff_2=dff_11.groupby('date_time',as_index=False)

    #dff_2['Event_number']= dff_2.groupby('date_time').cumcount()+1
     
    df_grouped_conv = dff_2.groupby(['conversion_status'])['conversion_status'].count()
    dff_grouped_conv=pd.DataFrame({'conversion_status':df_grouped_conv.index, 'count':df_grouped_conv.values})

    fig_conv= px.pie(dff_grouped_conv, names='conversion_status', values='count',title='Conversion Status in the given period')

    dff_timeline=dff_2

    flag=1

    if top_level_category_name_label is not None and len(top_level_category_name_label)!=0:
        flag=0
        if 'top_level_category_name' not in req_attr:
            top_level_category_name_label=[]
            flag=1
        else:
            dff_timeline=dff_2.loc[dff_2.top_level_category_name.isin(top_level_category_name_label)]
        print("cate: ")
        print(top_level_category_name_label)
        

    if click_browser_label is not None and len(click_browser_label)!=0:
        
        flag=0
        if 'click_browser' not in req_attr:
            click_browser_label =[]
            flag=1
        else:
            dff_timeline=dff_timeline.loc[dff_timeline.click_browser.isin(click_browser_label)]

        print("browser: ")
        print(click_browser_label)
    
    if enriched_country_label is not None and len(enriched_country_label)!=0:
        flag=0
        if 'enriched_country' not in req_attr:
            enriched_country_label =[]
            flag=1
        else:
            dff_timeline=dff_timeline.loc[dff_timeline.enriched_country.isin(enriched_country_label)]
        print("country: ")
        print(enriched_country_label)
    
    dff_timeline['Event_number']= dff_timeline.groupby('date_time').cumcount()+1
    dff_timeline['conversion_status']=dff_timeline['conversion_status'].astype(str)
    if flag==1:
        #fig_timeline =px.scatter(dff_2,x='in_date', y='hour',hover_data=req_attr)
        fig_timeline =px.scatter(dff_timeline,x='date_time', y='Event_number',color='conversion_status',hover_data=req_attr)
    else:
        #fig_timeline =px.scatter(dff_timeline,x='in_date', y='hour',hover_data=req_attr)
        fig_timeline =px.scatter(dff_timeline,x='date_time', y='Event_number',color='conversion_status',hover_data=req_attr)
        
    #top_level_category_name_label=[]
    #click_browser_label =[]
    #enriched_country_label =[]

    fig_timeline.update_yaxes(visible=False, showticklabels=False)

    df_grouped = dff_2.groupby(['enriched_country'])['enriched_country'].count()
    dff_3=pd.DataFrame({'enriched_country':df_grouped.index, 'count':df_grouped.values})

    fig = px.pie(dff_3, values='count', names='enriched_country', title='Population of European continent')
    return  fig_timeline,fig,fig_conv,#dash_table.DataTable(dff_2.to_dict('records'), [{"name": i, "id": i} for i in dff_2.columns])



if __name__ == '__main__':
    app.run_server(debug=True)

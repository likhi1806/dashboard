# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
#import _tkinter
#from tkinter.tix import DisplayStyle
from dash import Dash, html, dcc, Input, Output,dash_table,State, ALL
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
new_df=new_df.sort_values(by=['visitor_id','date_time'])
list_col = updated_cols
temp_list1 ={}
temp_list2 ={}
cnt=0
for col in list_col:
        temp_list1[col]=html.Div([html.Label(col,id={
                'type': 'dynamic-output_label',
                'index': cnt
            }),],style={'display':'block'})

        temp_list2[col]=html.Div([dcc.Dropdown(id={
                'type': 'dynamic-output',
                'index': cnt
            },options=[i for i in new_df[col].unique()],multi=True)],style={'display':'block'})

        cnt+=1




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

    html.Div(children=[],id= 'dynamic_dropdown'),

    
    #html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.H4(children='Visitor Timeline'),

    dcc.Graph(id='timeline_graph'),
    html.Div(children=[],id='timeline_text',style={"maxHeight": "400px", "overflow": "scroll",'display':'flex'}),

    html.Div(id='timeline_text_pro',style={"maxHeight": "400px", "overflow": "scroll"}),

    html.Div([
        html.Div(children=[],id='dates',style={"maxHeight": "50px", "overflow": "scroll",'display':'flex'}),
        html.Div(children=[],id='div-1',style={"maxHeight": "400px", "overflow": "scroll",'display':'flex'}),

    ],style={"maxHeight": "500px", "overflow": "scroll"}),
    
    #html.Div(children=[],id='div-1',style={"maxHeight": "400px", "overflow": "scroll",'display':'flex'}),

    dcc.Graph(id='conv_status'),
    dcc.Graph(id='graph')  

    
    
],style={'display': 'flex', 'flex-direction': 'column'})

pre=[]
prev=[]

@app.callback(
    Output('dynamic_dropdown', 'children'),
   #Input('submit-button-state', 'n_clicks'),
    State('dynamic_dropdown', 'children'),
    Input('req_attr','value'))
def display_dropdowns(children,req_attr):
    children=[]
    #print(prev)
    #print(req_attr)

    #if prev is not None and len(prev)!=0:
    #    if prev[-1] is not None and len(prev[-1])!=0:
    #        for col in prev[-1]:
    #           if col not in req_attr:
    #                print("inprev")
    #               children.remove(temp_list1[col])
    #               children.remove(temp_list2[col]) 

    if req_attr is not None and len(req_attr)!=0:
        for col in req_attr:
            children.append(temp_list1[col])
            children.append(temp_list2[col])

    
   # prev.append(req_attr)
   # print(children)
    return children


cols_reqi=['hour','conversion_status','enriched_derived_device','enriched_derived_os','click_browser','click_state','click_city','top_level_category_name']

@app.callback(

    Output('timeline_graph','figure'),
    Output('graph','figure'),
    Output('conv_status', 'figure'),
    #Output('timeline_text','children'),
    #Output('timeline_text_pro','children'),
    #Output('dynamic_dropdown','children'),

    Output('div-1', 'children'),
    #Output('dates','children'),
    #Input('submit-button-state', 'n_clicks'),
    State('visitor_id', 'value'),
    State('start_date', 'value'),
    State('end_date', 'value'),
    State('req_attr','value'),
    State('timeline_text','children'),
    Input({'type': 'dynamic-output', 'index': ALL}, 'value'),
    State({'type': 'dynamic-output', 'index': ALL}, 'id')

    )
def dashboard(visitor_id,start_date,end_date,req_attr,children,id,values):
    
    dff = new_df[new_df['visitor_id']==visitor_id]
    dff_1 =dff[dff['ts_date']>=start_date]
    dff_2=dff_1[dff_1['ts_date']<=end_date]


     
    df_grouped_conv = dff_2.groupby(['conversion_status'])['conversion_status'].count()
    dff_grouped_conv=pd.DataFrame({'conversion_status':df_grouped_conv.index, 'count':df_grouped_conv.values})

    fig_conv= px.pie(dff_grouped_conv, names='conversion_status', values='count',title='Conversion Status in the given period')

    dff_timeline=dff_2

    for (i, value) in enumerate(values):
        if value is not None and len(value)!=0:
            #col=[]
            #col.append(list_col[value['index']])
            col=list_col[value['index']]
            print(col)
            print(value)
            print(id[i])
            if id[i] is not None and len(id[i])!=0:
                dff_timeline=dff_timeline.loc[dff_timeline[col].isin(id[i])]
    
    dff_timeline['Event_number']= dff_timeline.groupby('date_time').cumcount()+1
    dff_timeline['conversion_status']=dff_timeline['conversion_status'].astype(str)

    fig_timeline =px.scatter(dff_timeline,x='date_time', y='Event_number',color='conversion_status',hover_data=req_attr)
        
    #top_level_category_name_label=[]
    #click_browser_label =[]
    #enriched_country_label =[]

    fig_timeline.update_yaxes(visible=False, showticklabels=False)

    df_grouped = dff_2.groupby(['enriched_country'])['enriched_country'].count()
    dff_3=pd.DataFrame({'enriched_country':df_grouped.index, 'count':df_grouped.values})

    fig = px.pie(dff_3, values='count', names='enriched_country', title='Population of European continent')

    children=[]
    dff_grpdate=dff_2.groupby('ts_date')

    keys = dff_grpdate.groups.keys()

    dff_timeline['conversion_status']=dff_timeline['conversion_status'].astype(int)
  
    #for i in keys:
        #dff_tempo=dff_grpdate.get_group(i)
        #children.append(html.Div(i))
        #dff_tempo.reset_index(inplace=True)
        #children.append(dash_table.DataTable(dff_tempo.to_dict('records'),[{"name": i, "id": i} for i in dff_tempo.columns],fixed_rows={'headers': True},style_table={'overflow': 'scroll'},style_cell={'height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},))
        #print(dff_tempo)
    
    
    #for i in keys:
      #  child.append(html.Div(i))
    #dff_rw=[]
    for i in keys:
        child=[]
        dff_tempi=dff_grpdate.get_group(i)
        list_r=[]
        for index, row in dff_tempi.iterrows():
          finall=""
          for col in cols_reqi:
              finall=finall+col+": "+str(row[col])+" "
          list_r.append(finall)
        df_data =pd.DataFrame(list_r,columns =[i])
        #print(df_data)
        #finall=dff_tempi[cols_reqi].to_dict('records')
        dff_tempo=dff_tempi[cols_reqi]
        #dff_rw.append(finall)
        child.append(html.Div(i))
        rd=df_data.to_dict('records')
        child.append(dash_table.DataTable(dff_tempo.to_dict('records'), [{"name": i, "id": i} for i in dff_tempo.columns],fixed_rows={'headers': True},style_table={'overflowX': 'auto'},style_cell={'height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},style_data_conditional=[
        {
            'if': {
                'filter_query': '{conversion_status}>=1',
            },
            'backgroundColor': '#FF4136',
            'color': 'white'
        },
    ]))
        children.append(html.Div(child))
    #dffr=[]
    #chi=[]
    #dffr.append(dff_rw)
    #print(len(dff_rw))
    #df_data =pd.DataFrame(dffr,columns = keys)
    #chi.append(dash_table.DataTable(df_data.to_dict('records'),[{"name": i, "id": i} for i in df_data.columns],fixed_rows={'headers': True},style_table={'overflowX': 'auto'},style_cell={'height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},))


    return  fig_timeline,fig,fig_conv,children#,child



if __name__ == '__main__':
    app.run_server(debug=True)
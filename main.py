import pandas as pd
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

folder = r'W:\Projekte\MAXCoat_61906\04_Bearbeitung\in-situ PEMFC\MS2\S316LwCoating'

files = ['maxcoat_ss_coating_#01_20220729.txt',
         'maxcoat_ss_coating_#01_20220730.txt',
         'maxcoat_ss_coating_#01_20220731.txt',
         'maxcoat_ss_coating_#01_20220801.txt',
         'maxcoat_ss_coating_#01_20220802.txt',
         'maxcoat_ss_coating_#01_20220803.txt',
         'maxcoat_ss_coating_#01_20220804.txt',
         'maxcoat_ss_coating_#01_20220805.txt']

dfs = [pd.read_csv(folder + '/' + f, encoding='cp1252', delimiter='\t', decimal=',') for f in files]

df = pd.concat(dfs, ignore_index=True)

df['timer'] = pd.to_datetime(df['Datum / Uhrzeit'], format='%d.%m.%y %H:%M:%S')
df = df.set_index('timer')
starttime = df.index[0]


# df = df[(df.index < '2022-07-30 13:48:23') | (df.index > '2022-08-02 09:53:22')]

# duration = 0
# timestamp1 = '2022-07-30 13:48:23'
# timestamp2 = '2022-08-02 09:53:22'

# for i in range(0, len(df)-1):
#     if df.index[i] < datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S'):
#         duration = df.index[i] - starttime
#         print(duration)
#         df['t elapsed [s]'] = duration
#     if df.index[i] > datetime.strptime(timestamp2, '%Y-%m-%d %H:%M:%S') :
#         df['t elapsed [s]'] = df.index[i] - datetime.strptime(timestamp2, '%Y-%m-%d %H:%M:%S') + duration
#     else:
#         df['t elapsed [s]'] = None


# time = df['t elapsed [s]']
timer = df.index
df['current density [A/cm2]'] = round(df['I Summe [A]'] / 25,2)

# parameters fig1
voltage = df['AI.U.E.Co.Tb.1 [V]']
temperature = df['AI.T.Air.ST.UUT.out [°C]']
hfr = df['HFR [mOhm]'].apply(lambda x: x if x != -99 and x < 100 else None)
current_density = df['current density [A/cm2]']

# parameters fig2
df2 = df[df['Kommentar'] == 'ui1_messen']
current_densities = pd.unique(df2['current density [A/cm2]'])

for i in range(0, len(df)):
    if df['Kommentar'][i] == 'u1_messen':
        pol_date = df.index[i]


mean_voltages = []
for j in current_densities:
    mean_voltages.append(
        df2[df2['current density [A/cm2]'] == j]['AI.U.E.Co.Tb.1 [V]'].mean())



#fig1
fig_main = make_subplots(specs=[[{"secondary_y": True}]])

fig_main.add_trace(
    go.Scatter(x=timer, y=current_density, name="current density [A/cm2]"),
    secondary_y=False,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=voltage, name="voltage [V]"),
    secondary_y=True,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=temperature, name="temperature [°C]"),
    secondary_y=True,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=hfr, name='HFR [mOhm]'),
    secondary_y=True,
)

fig_main.update_layout(width=1200, height=600)


#fig2
fig_pol = make_subplots(specs=[[{"secondary_y": True}]])

fig_pol.add_trace(
    go.Scatter(x=current_densities, y=mean_voltages, name="mean_voltage [V]"),
    secondary_y=False,
)

# fig_main.add_trace(
#     go.Scatter(x=timer, y=voltage, name="voltage [V]"),
#     secondary_y=True,
# )



# dash
import dash
from dash import dcc
from dash import html

app = dash.Dash()

app.layout = html.Div([
    html.H1('IGF MAXCoat (in-situ PEMFC Testing)', style={'textAlign': 'center'}),
    html.Div('Data of Testrig Parameters'),
    dcc.Graph(id='main-data', figure=fig_main),
    dcc.Graph(id='pol-data', figure=fig_pol),
])

app.run_server(debug=True, port=8050, host='0.0.0.0')
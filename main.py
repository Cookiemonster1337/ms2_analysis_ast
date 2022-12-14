import pandas as pd
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import plotly.figure_factory as ff

# ----------------------------------------------------------------------------------------------------------------------
# DATA IMPORT
# ----------------------------------------------------------------------------------------------------------------------
testrig_folder = r'W:\Projekte\MAXCoat_61906\04_Bearbeitung\in-situ PEMFC\MS2\S316LwCoating\testrig'
gamry_folder = r'W:\Projekte\MAXCoat_61906\04_Bearbeitung\in-situ PEMFC\MS2\S316LwCoating\gamry'
info_folder = r'W:\Projekte\MAXCoat_61906\04_Bearbeitung\in-situ PEMFC\MS2'

# INFO FILE
df_info = pd.read_csv(info_folder + '/' + 'info.txt', encoding='cp1252', delimiter='\t', decimal=',')

# TESTRIG FILES
testrig_files = ['maxcoat_ss_coating_#01_20220729.txt',
         'maxcoat_ss_coating_#01_20220730.txt',
         'maxcoat_ss_coating_#01_20220731.txt',
         'maxcoat_ss_coating_#01_20220801.txt',
         'maxcoat_ss_coating_#01_20220802.txt',
         'maxcoat_ss_coating_#01_20220803.txt',
         'maxcoat_ss_coating_#01_20220804.txt',
         'maxcoat_ss_coating_#01_20220805.txt',
         'maxcoat_ss_coating_#01_20220806.txt',
         'maxcoat_ss_coating_#01_20220807.txt',
         'maxcoat_ss_coating_#01_20220808.txt']

dfs = [pd.read_csv(testrig_folder + '/' + f, encoding='cp1252', delimiter='\t', decimal=',') for f in testrig_files]
df = pd.concat(dfs, ignore_index=True)

# EIS FILES
eis_files = [f for f in os.listdir(gamry_folder) if 'EIS' in f]

# CV FILES
cv_files = [f for f in os.listdir(gamry_folder) if 'CV' in f]

# DICTIONARY
meas_characteristics = {}

# ----------------------------------------------------------------------------------------------------------------------
# DATAFRAMES
# ----------------------------------------------------------------------------------------------------------------------

# TESTRIG / IV DATAFRAME
df['timer'] = pd.to_datetime(df['Datum / Uhrzeit'], format='%d.%m.%y %H:%M:%S')
df = df.set_index('timer')
starttime = df.index[0]
timer = df.index
df = df.reset_index()
df['current density [A/cm2]'] = round(df['I Summe [A]'] / 25, 2)
df['mean current density [A/cm2]'] = 0

comment_marker = ''
start_marker = 0
for i in range(0, len(df)):
    if df['Kommentar'][i] != comment_marker:
        comment_marker = df['Kommentar'][i]
        df['mean current density [A/cm2]'][start_marker:i-1] = df['current density [A/cm2]'][start_marker:i-1].mean()
        start_marker = i

# EIS DATAFRAMES

columns = ['index', 'datapoints [#]', 'time [s]', 'frequency [Hz]',
          'Z_real [Ohm]', 'Z_imag [Ohm]', 'Z_sig [V]', 'Zmod [ohm]',
          'Z_phz [??C]', 'I_DC [A]', 'V_DC [V]', 'IE_Range [#]']
eis_dfs = [pd.read_csv(gamry_folder + '/' + f, encoding='cp1252',
                       delimiter='\t', decimal=',', skiprows=22, dtype=float,
                       names=columns) for f in eis_files]


# CV DATAFRAMES
cv1_dfs = [pd.read_csv(gamry_folder + '/' + f, encoding='cp1252',
                       delimiter='\t', decimal=',', skiprows=21, dtype=float, usecols=[1, 2, 3]
                      ) for f in cv_files if 'CV1.1' in f]

cv2_dfs = [pd.read_csv(gamry_folder + '/' + f, encoding='cp1252',
                       delimiter='\t', decimal=',', skiprows=21, dtype=float, usecols=[1, 2, 3]
                      ) for f in cv_files if 'CV1.2' in f]

cv3_dfs = [pd.read_csv(gamry_folder + '/' + f, encoding='cp1252',
                       delimiter='\t', decimal=',', skiprows=21, dtype=float, usecols=[1, 2, 3]
                      ) for f in cv_files if 'CV1.3' in f]

cv4_dfs = [pd.read_csv(gamry_folder + '/' + f, encoding='cp1252',
                       delimiter='\t', decimal=',', skiprows=21, dtype=float, usecols=[1, 2, 3]
                      ) for f in cv_files if 'CV1.4' in f]

# ----------------------------------------------------------------------------------------------------------------------
# TABLE SPECS
# ----------------------------------------------------------------------------------------------------------------------

# fig_info = go.Figure(data=[go.Table(
#     header=dict(values=list(df_info),
#                 fill_color='paleturquoise',
#                 align='left'),
#     cells=dict(values=[df_info['Parameters'], df_info['Values']],
#                fill_color='lavender',
#                align='left'))
# ])

# ----------------------------------------------------------------------------------------------------------------------
# FIGURE - MAIN
# ----------------------------------------------------------------------------------------------------------------------

voltage = df['AI.U.E.Co.Tb.1 [V]']
temperature = df['AI.T.Air.ST.UUT.out [??C]']
hfr = df['HFR [mOhm]'].apply(lambda x: x if x != -99 and x < 20 else None)
current_density = df['current density [A/cm2]']

# eis_markers = df.index[df['Kommentar'] == '#EIS#'].tolist()
# cv_markers = df.index[df['Kommentar'] == '#CV#'].tolist()

fig_main = make_subplots(rows=2, cols=1, row_heights=[0.3, 0.7], vertical_spacing=0.03, specs=[[{"type": "table"}],
           [{"type": "scatter"}]])

fig_main.add_trace(
    go.Table(
        header=dict(values=list(df_info),
                    fill_color='lightblue',
                    align='left',
                    font=dict(size=10),),
        cells=dict(values=[df_info['Parameters'], df_info['Values']],
                   fill_color='lightgrey',
                   align='right',
                   font=dict(size=10),)),
    row=1, col=1,
)

# fig_main.add_trace(ff.create_table(df_info), row=1, col=1)

fig_main.add_trace(
    go.Scatter(x=timer, y=current_density, name="current density [A/cm2]"),
    row=2, col=1,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=voltage, name="voltage [V]"),
    row=2, col=1,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=temperature, name="temperature [??C]"),
    row=2, col=1,
)

fig_main.add_trace(
    go.Scatter(x=timer, y=hfr, name='HFR [mOhm]'),
    row=2, col=1,
)

fig_main.update_layout(width=1200, height=800)


# ----------------------------------------------------------------------------------------------------------------------
# FIGURE - IV-CURVE
# ----------------------------------------------------------------------------------------------------------------------

iv_markers = df.index[df['Kommentar'] == '#IV-CURVE#'].tolist()

fig_pol = make_subplots(x_title='current density [A/cm2]', y_title='voltage [V]')

for i in range(0, len(iv_markers)):

    if i == len(iv_markers) - 1:
        df_iv = df.iloc[iv_markers[i]:]
    else:
        df_iv = df.iloc[iv_markers[i]: iv_markers[i + 1]]

    df_iv = df_iv[df_iv['Kommentar'] == 'ui1_messen']

    df_iv = df_iv[df_iv['current density [A/cm2]'] != 1.19]

    current_densities = pd.unique(df_iv['current density [A/cm2]'])


    mean_voltages = []

    for j in current_densities:
        mean_voltages.append(
            df_iv[df_iv['current density [A/cm2]'] == j]['AI.U.E.Co.Tb.1 [V]'].mean())



    iv_name = '#' + str(i+1) + ' @ ' + df['Datum / Uhrzeit'][iv_markers[i]]

    fig_pol.add_trace(
        go.Scatter(x=current_densities, y=mean_voltages, name=iv_name, )
    )

fig_pol.update_layout(width=1200, height=600)




# ----------------------------------------------------------------------------------------------------------------------
# FIGURE - AST
# ----------------------------------------------------------------------------------------------------------------------

ast_markers = df.index[df['Kommentar'] == '#AST-CYCLE#'].tolist()

fig_ast = make_subplots(x_title='duration [h]', y_title='current density [A/cm??]', specs=[[{"secondary_y": True}]])
# fig_deg = make_subplots(x_title='cycle [#]', y_title='mean current density [A/cm??]')

deg_600mV = []
deg_400mV = []
deg_timer = []

for i in range(0, len(ast_markers)):

    df_ast = df.iloc[ast_markers[i]:iv_markers[i+1]]

    # comment_marker = ''
    # comment_index = 0
    # for i in range(0, len(df_ast)):
    #     if df_ast['Kommentar'] != comment_marker:
    #         comment_index = i
    #         df_ast['mean current density [A/cm2]'] = df_ast[]

    exclusions = ['anfahren_10A', 'anfahren_20A', 'ocv', 'anfahren_I_High', 'anfahren_I_Low', 'halten_I_Low',
                 'halten_I_High']

    df_ast = df_ast[~df_ast['Kommentar'].isin(exclusions)]

    df_ast = df_ast.reset_index()

    current_density = df_ast['current density [A/cm2]']

    mean_current_density = df_ast['mean current density [A/cm2]']

    ast_start = df_ast['T relativ [min]'][0]

    df_ast['t elapsed [s]'] = (df_ast['T relativ [min]'] - ast_start) / 60

    duration = df_ast['t elapsed [s]']

    voltage = df_ast['AI.U.E.Co.Tb.1 [V]']

    deg_600mV.append(df_ast[df_ast['Kommentar'] == 'operation@0.6V']['mean current density [A/cm2]'].mean())
    deg_400mV.append(df_ast[df_ast['Kommentar'] == 'operation@0.4V']['mean current density [A/cm2]'].mean())
    deg_timer.append(i*25)

# PLOT AST

    ast_name = '#' + str(i) + ' @ ' + df['Datum / Uhrzeit'][ast_markers[i]][:-9]

    # fig_ast.add_trace(
    #     go.Scatter(x=duration, y=current_density, name=ast_name + ' j'),
    #     secondary_y=False,
    # )

    fig_ast.add_trace(
        go.Scatter(x=duration, y=mean_current_density, name=ast_name + ' j mean'),
        secondary_y=False,
    )

    # fig_ast.add_trace(
    #     go.Scatter(x=duration, y=voltage, name=ast_name + ' U'),
    #     secondary_y=True,
    # )

fig_ast.update_layout(width=1200, height=600)

# ----------------------------------------------------------------------------------------------------------------------
# FIGURE - DEG
# ----------------------------------------------------------------------------------------------------------------------
import plotly.express as px

df_deg = pd.DataFrame(data={'deg_@400mV': deg_400mV, 'deg_@600mV': deg_600mV}, index=deg_timer)

fig_deg_ast = px.scatter(df_deg, trendline='ols', labels={'x': 'time [h]', 'y': 'mean current density [A/cm2]'})

# time = df[df['Kommentar'] == 'operation @ 0.4V']['timer']
# j_400mv = df[df['Kommentar'] == 'operation @ 0.4V']['current density [A/cm2]']



fig_deg_ast.update_layout(width=1200, height=600)


# ----------------------------------------------------------------------------------------------------------------------
# FIGURE - EIS
# ----------------------------------------------------------------------------------------------------------------------

fig_eis = make_subplots(x_title='impedance (real) [Ohm*cm2]', y_title='impedance (imag) [Ohm*cm2]')

for i in range(0, len(eis_dfs)):
    eis_df = eis_dfs[i]

    impedance_real = eis_df['Z_real [Ohm]'] * 25
    impedance_imag = eis_df['Z_imag [Ohm]'] * -25

    eis_name = eis_files[i][-20:-8]

    fig_eis.add_trace(
        go.Scatter(x=impedance_real, y=impedance_imag, mode = 'markers', name=eis_name)
    )

fig_eis.update_layout(width=1200, height=600)


# ----------------------------------------------------------------------------------------------------------------------
# FIGURE CV
# ----------------------------------------------------------------------------------------------------------------------

fig_cv1 = make_subplots(x_title='Potential vs. Hydrogen Anode [V]', y_title='Current [A]')

for i in range(0, len(cv1_dfs)):
    cv_df = cv1_dfs[i]

    voltage = cv_df['voltage [V]'][38571:]*-1
    current = cv_df['current [A]'][38571:]*-1

    cv_name = '#' + str(i) + ' ' + cv_files[i][-20:-8]

    fig_cv1.add_trace(
        go.Scatter(x=voltage, y=current, name=cv_name)
    )

fig_cv1.update_layout(width=1200, height=600)

fig_cv2 = make_subplots(x_title='Potential vs. Hydrogen Anode [V]', y_title='Current [A]')

for i in range(0, len(cv2_dfs)):
    cv_df = cv2_dfs[i]

    voltage = cv_df['voltage [V]'][45151:]*-1
    current = cv_df['current [A]'][45151:]*-1

    cv_name = '#' + str(i) + ' ' + cv_files[i][-20:-8]

    fig_cv2.add_trace(
        go.Scatter(x=voltage, y=current, name=cv_name)
    )

fig_cv2.update_layout(width=1200, height=600)

fig_cv3 = make_subplots(x_title='Potential vs. Hydrogen Anode [V]', y_title='Current [A]')

for i in range(0, len(cv3_dfs)):
    cv_df = cv3_dfs[i]

    voltage = cv_df['voltage [V]'][47529:]*-1
    current = cv_df['current [A]'][47529:]*-1

    cv_name = '#' + str(i) + ' ' + cv_files[i][-20:-8]

    fig_cv3.add_trace(
        go.Scatter(x=voltage, y=current, name=cv_name)
    )

fig_cv3.update_layout(width=1200, height=600)

fig_cv4 = make_subplots(x_title='Potential vs. Hydrogen Anode [V]', y_title='Current [A]')

for i in range(0, len(cv4_dfs)):
    cv_df = cv4_dfs[i]

    voltage = cv_df['voltage [V]'][44885:]*-1
    current = cv_df['current [A]'][44885:]*-1

    cv_name = '#' + str(i) + ' ' + cv_files[i][-20:-8]

    fig_cv4.add_trace(
        go.Scatter(x=voltage, y=current, name=cv_name)
    )

fig_cv4.update_layout(width=1200, height=600)


# ----------------------------------------------------------------------------------------------------------------------
# DASH
# ----------------------------------------------------------------------------------------------------------------------
import dash
from dash import dcc
from dash import html

app = dash.Dash()

app.layout = html.Div([
    html.H1('IGF MAXCoat (in-situ PEMFC-AST Testing)', style={'textAlign': 'center'}),

    html.Div(['Data of Testrig Parameters',
    dcc.Graph(id='main-data', figure=fig_main),]),

    html.Div(['AST Load Cycling',
    dcc.Graph(id='ast-data', figure=fig_ast),]),

    html.Div(['AST Degradation',
              dcc.Graph(id='deg-data', figure=fig_deg_ast), ]),

    html.Div(['IV-Curve in between AST',
    dcc.Graph(id='pol-data', figure=fig_pol),]),

    html.Div(['EIS in between AST',
    dcc.Graph(id='eis-data', figure=fig_eis),]),

    html.Div(['CV-I in between AST (-0.05 to -0.9V @ 100mV/s)',
              dcc.Graph(id='cv1-data', figure=fig_cv1), ]),

    html.Div(['CV-II in between AST (0 to -0.9V @ 100mV/s)',
              dcc.Graph(id='cv2-data', figure=fig_cv2), ]),

    html.Div(['CV-III in between AST  (0 to -0.9V @ 20mV/s)',
              dcc.Graph(id='cv3-data', figure=fig_cv3), ]),

    html.Div(['CV-IV in between AST  (-0.05 to -0.9V @ 20mV/s)',
              dcc.Graph(id='cv4-data', figure=fig_cv4), ]),
])

app.run_server(debug=True, port=8050, host='0.0.0.0')
import dash
from dash import dcc, html, Input, Output, State, ALL
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import io
import base64

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Лабораторна робота: Plotly Dash"

def parse_image(contents):
    if contents is None:
        return None
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return Image.open(io.BytesIO(decoded))

def extract_features(img_pil, rows=5, cols=5, threshold=128):
    img_gray = img_pil.convert('L')
    img_np = np.array(img_gray)
    h, w = img_np.shape

    cell_h, cell_w = h / rows, w / cols
    abs_vector = []

    for r in range(rows):
        for c in range(cols):
            r_start, r_end = int(r * cell_h), int((r + 1) * cell_h)
            c_start, c_end = int(c * cell_w), int((c + 1) * cell_w)
            cell = img_np[r_start:r_end, c_start:c_end]
            abs_vector.append(np.sum(cell < threshold))

    abs_vector = np.array(abs_vector, dtype=float)
    total_sum = np.sum(abs_vector)
    norm_vector = abs_vector / total_sum if total_sum > 0 else abs_vector.copy()

    return abs_vector, norm_vector, img_np, h, w

def calculate_distance(vec1, vec2, norm_type="Евклідова"):
    if norm_type == "Евклідова":
        return np.sqrt(np.sum((vec1 - vec2) ** 2))
    elif norm_type == "Норма Чебишева":
        return np.max(np.abs(vec1 - vec2))
    elif norm_type == "Мангеттенська":
        return np.sum(np.abs(vec1 - vec2))

app.layout = html.Div([
    html.H1("🧠 Розпізнавання Образів (Plotly Dash)", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    
    dcc.Tabs(id="tabs-tasks", value='tab-1', children=[
        dcc.Tab(label='Завдання 1: Вектори ознак', value='tab-1'),
        dcc.Tab(label='Завдання 2: Еталонне розпізнавання', value='tab-2'),
        dcc.Tab(label='Завдання 3: Система з навчанням', value='tab-3'),
    ]),
    
    html.Div(id='tabs-content', style={'padding': '20px', 'fontFamily': 'Arial'})
])

@app.callback(Output('tabs-content', 'children'), Input('tabs-tasks', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3("Завдання 1: Побудова векторів ознак (Сітка 5x5)"),
            dcc.Upload(
                id='upload-task1',
                children=html.Div(['Перетягніть або ', html.A('Завантажте .BMP / .PNG зображення')]),
                style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '2px',
                       'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'marginBottom': '20px'}
            ),
            html.Div(id='output-task1')
        ])
    
    elif tab == 'tab-2':
        return html.Div([
            html.H3("Завдання 2: Класифікація методом порівняння з еталоном"),
            html.Label("Оберіть метрику відстані:"),
            dcc.Dropdown(
                id='metric-select',
                options=[
                    {'label': 'Евклідова норма', 'value': 'Евклідова'},
                    {'label': 'Норма Чебишева', 'value': 'Норма Чебишева'},
                    {'label': 'Мангеттенська норма', 'value': 'Мангеттенська'}
                ],
                value='Евклідова', style={'width': '300px', 'marginBottom': '20px'}
            ),
            html.Div([
                html.Div([html.H5("Еталон Класу 1"), dcc.Upload(id='u-e1', children=html.Button('Завантажити E1'))], style={'display': 'inline-block', 'marginRight': '30px'}),
                html.Div([html.H5("Еталон Класу 2"), dcc.Upload(id='u-e2', children=html.Button('Завантажити E2'))], style={'display': 'inline-block', 'marginRight': '30px'}),
                html.Div([html.H5("Еталон Класу 3"), dcc.Upload(id='u-e3', children=html.Button('Завантажити E3'))], style={'display': 'inline-block'}),
            ]),
            html.Hr(),
            html.H5("Невідомий образ для класифікації:"),
            dcc.Upload(id='u-test2', children=html.Button('Завантажити тестовий образ')),
            html.Div(id='output-task2', style={'marginTop': '20px'})
        ])

    elif tab == 'tab-3':
        return html.Div([
            html.H3("Завдання 3: Система розпізнавання з навчанням"),
            html.P("Завантажте по 2 або більше зображень для кожного класу:"),
            html.Div([
                html.Div([html.H5("Навчання Клас 1"), dcc.Upload(id='u-c1', children=html.Button('Файли Клас 1'), multiple=True)], style={'display': 'inline-block', 'marginRight': '30px'}),
                html.Div([html.H5("Навчання Клас 2"), dcc.Upload(id='u-c2', children=html.Button('Файли Клас 2'), multiple=True)], style={'display': 'inline-block', 'marginRight': '30px'}),
                html.Div([html.H5("Навчання Клас 3"), dcc.Upload(id='u-c3', children=html.Button('Файли Клас 3'), multiple=True)], style={'display': 'inline-block'}),
            ]),
            html.Hr(),
            html.H5("Тестовий образ:"),
            dcc.Upload(id='u-test3', children=html.Button('Завантажити тестовий образ')),
            html.Div(id='output-task3', style={'marginTop': '20px'})
        ])


@app.callback(Output('output-task1', 'children'), Input('upload-task1', 'contents'))
def update_task1(contents):
    if not contents:
        return html.Div("Будь ласка, завантажте зображення.")
    
    img_pil = parse_image(contents)
    abs_vec, norm_vec, img_np, h, w = extract_features(img_pil)

    fig_img = px.imshow(img_np, color_continuous_scale='gray')
    for r in range(1, 5):
        fig_img.add_shape(type="line", x0=-0.5, y0=r*(h/5)-0.5, x1=w-0.5, y1=r*(h/5)-0.5, line=dict(color="Red", width=2))
    for c in range(1, 5):
        fig_img.add_shape(type="line", x0=c*(w/5)-0.5, y0=-0.5, x1=c*(w/5)-0.5, y1=h-0.5, line=dict(color="Red", width=2))

    fig_bar = px.bar(x=list(range(1, 26)), y=norm_vec, labels={'x': 'Комірка (1-25)', 'y': 'Частка'}, title="Нормований вектор")

    return html.Div([
        html.Div([
            dcc.Graph(figure=fig_img, style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(figure=fig_bar, style={'width': '48%', 'display': 'inline-block'})
        ]),
        html.H4("Абсолютний вектор X:"),
        html.Pre(str([int(x) for x in abs_vec]), style={'backgroundColor': '#f4f4f4', 'padding': '10px'}),
        html.H4("Нормований вектор X_norm:"),
        html.Pre(str([round(float(x), 4) for x in norm_vec]), style={'backgroundColor': '#f4f4f4', 'padding': '10px'})
    ])

@app.callback(
    Output('output-task2', 'children'),
    [Input('u-e1', 'contents'), Input('u-e2', 'contents'), Input('u-e3', 'contents'), Input('u-test2', 'contents'), Input('metric-select', 'value')]
)
def update_task2(e1, e2, e3, test, metric):
    if not (e1 and e2 and e3 and test):
        return html.Div("Завантажте всі 3 еталони та тестове зображення.")

    e_vecs = [extract_features(parse_image(e))[1] for e in [e1, e2, e3]]
    _, test_vec, _, _, _ = extract_features(parse_image(test))

    dists = [calculate_distance(test_vec, ev, metric) for ev in e_vecs]
    best_class = np.argmin(dists) + 1

    return html.Div([
        html.H4(f"Відстань до Класу 1: {dists[0]:.4f}"),
        html.H4(f"Відстань до Класу 2: {dists[1]:.4f}"),
        html.H4(f"Відстань до Класу 3: {dists[2]:.4f}"),
        html.H3(f"🏆 Висновок: Образ належить до КЛАСУ {best_class}", style={'color': 'green'})
    ])

@app.callback(
    Output('output-task3', 'children'),
    [Input('u-c1', 'contents'), Input('u-c2', 'contents'), Input('u-c3', 'contents'), Input('u-test3', 'contents')]
)
def update_task3(c1_list, c2_list, c3_list, test):
    if not (c1_list and c2_list and c3_list and test):
        return html.Div("Завантажте серію зображень для кожного класу та тестове зображення.")

    centers = []
    for c_list in [c1_list, c2_list, c3_list]:
        vecs = [extract_features(parse_image(f))[1] for f in c_list]
        centers.append(np.mean(vecs, axis=0))

    _, test_vec, _, _, _ = extract_features(parse_image(test))
    dists = [calculate_distance(test_vec, center, "Евклідова") for center in centers]
    best_class = np.argmin(dists) + 1

    return html.Div([
        html.H4(f"Центр Класу 1: {np.round(centers[0], 3).tolist()}"),
        html.H4(f"Центр Класу 2: {np.round(centers[1], 3).tolist()}"),
        html.H4(f"Центр Класу 3: {np.round(centers[2], 3).tolist()}"),
        html.H3(f"🏆 Результат навчання: Образ віднесено до КЛАСУ {best_class}", style={'color': 'blue'})
    ])

if __name__ == '__main__':
    app.run(debug=True)
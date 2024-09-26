import mne
import plotly.graph_objects as go
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Настройка CORS
origins = [
    "http://localhost:5173",
    "http://localhost:81" # Разрешить доступ с этого домена
    # Добавьте другие домены, если необходимо
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешенных доменов
    allow_credentials=True,
    allow_methods=["*"],     # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],     # Разрешить все заголовки
)


@app.post("/uploadfile")
async def upload_and_post_file(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    raw = mne.io.read_raw_bdf(file_location, preload=True)
    raw.pick_types(eeg=True)
    raw.crop(tmin=0, tmax=180)  # Выбор временного интервала от 0 до 180 секунд

    # Получение данных для графика
    data, times = raw[:, :]

    # Создание интерактивного графика
    fig = go.Figure()
    for i in range(data.shape[0]):
        fig.add_trace(go.Scatter(
            x=times, y=data[i], mode='lines', name=raw.ch_names[i]))

    # Сохранение графика в HTML
    output_file = 'plot.html'
    fig.write_html(output_file)

    # Удаление временного файла
    if os.path.exists(file_location):
        os.remove(file_location)

    # Возврат HTML файла
    with open(output_file, 'rb') as f:
        html_content = f.read()

    # Удаление HTML файла после отправки
    if os.path.exists(output_file):
        os.remove(output_file)

    return HTMLResponse(content=html_content)
    


# raw = mne.io.read_raw_bdf('C:\\Users\\Паша\\VSProjects\\eeg\\backend\\example.bdf', preload=True)


# raw.pick_types(eeg=True)  # Выбор только EEG каналов
# raw.crop(tmin=0, tmax=180)  # Выбор временного интервала от 0 до 60 секунд


# data, times = raw[:, :]


# fig = go.Figure()
# for i in range(data.shape[0]):
#     fig.add_trace(go.Scatter(
#         x=times, y=data[i], mode='lines', name=raw.ch_names[i]))

# output_file = 'plot.html'
# fig.write_html(output_file)


# if os.path.exists(output_file):  
#     os.remove(output_file)  
#     print(f'Файл {output_file} был удален.')
# else:
#     print(f'Файл {output_file} не найден.')
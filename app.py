
import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/' ,methods=["GET", "POST"])
def index():
    if request.method == "GET":
        print("\nholi")
        return render_template("index.html",dataframe=None)
    else:
        print("\nPOST")

        archivo = request.files['file']
        if archivo.filename == '':
            return "No se ha seleccionado ningún archivo."

        if archivo:
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            df = pd.read_excel(archivo_path)
            print(df)  #
            
        
        
        return render_template('index.html',dataframe=df)

@app.route('/plot')
def plot():
    # Crear datos y diagrama de caja
    data = [np.random.normal(0, std, 100) for std in range(1, 5)]
    fig, ax = plt.subplots()
    ax.boxplot(data, vert=True, patch_artist=True)
    plt.xticks(np.arange(1, len(data) + 1), ['A', 'B', 'C', 'D'])
    plt.xlabel('Grupos')
    plt.ylabel('Valores')
    plt.title('Diagrama de Caja')

    # Convertir el gráfico en una imagen base64
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')
    plt.close()

    return render_template('plot.html', img_base64=img_base64)



if __name__ == '__main__':
    app.debug = True
    app.run()
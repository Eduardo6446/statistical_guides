
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
        return render_template("index.html",dataframe=None,max =None,min=None,rango=None,n=None,k=None,L=L)
    else:
        # Tomamos el archivo del input
        archivo = request.files['file']

        # validamos si se seleccionó
        if archivo.filename == '':
            return "No se ha seleccionado ningún archivo."

        #si hay un archivo, lo guardamos en la carpeta uploads y lo guardamos en una variable
        if archivo:
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            df = pd.read_excel(archivo_path)

        #Reemplazamos las comas por puntos
        df.replace(',', '.', regex=True, inplace=True)
        df = df.apply(pd.to_numeric)

        #Formulas
        #Numero de datos
        n = df.count().sum()

        #Valor maximo    
        max = df.max().max()

        #Valor minimo
        min = df.min().min()

        #Rango
        rango = max - min

        #Clases o intervalos
        k = np.sqrt(n)

        #Redondeado al entero mas cercano
        k = round(k)

        #Longitud
        L = rango / k

        # Valor específico para el que deseas calcular la frecuencia 
        valor_especifico = 5 

        # Calcula la frecuencia absoluta del valor específico en la columna
        ##frecuencia_absoluta = df['columna_name'].value_counts()[valor_especifico]

        # Calcula el número total de observaciones en la columna
        ##total_observaciones = len(df['columna_name'])

        # Calcula la frecuencia relativa
        ##frecuencia_relativa = frecuencia_absoluta / total_observaciones

        # Calcula la frecuencia absoluta de cada valor en la columna y suma acumulada
        ##frecuencia_acumulada_absoluta = df['columna_name'].value_counts().sort_index().cumsum()

        # Obtén la frecuencia absoluta acumulada para el valor específico
        ##frecuencia_absoluta_acumulada_valor = frecuencia_acumulada_absoluta.get(valor_especifico, 0)

        # Calcula la frecuencia relativa acumulada dividiendo por el total de observaciones

        ##total_observaciones = len(df['columna_name'])
        ##frecuencia_relativa_acumulada_valor = frecuencia_absoluta_acumulada_valor / total_observaciones

        
        return render_template('index.html',dataframe=df, max=max,min=min,rango=rango,n=n,k=k,L=L)

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
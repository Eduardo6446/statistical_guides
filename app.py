
from math import ceil, floor, log10
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

#DataFrame
table = pd.DataFrame(columns=[
    'Numero',
    'Clase',
    'Marcas de clase',
    'Frecuencia absoluta',
    'Frecuencia absoluta acumulada',
    'Frecuencia relativa',
    'Frecuencia relativa acumulada',
])


#datos
data = []



#Listas


#Frecuencia absoluta
fabs  = []

#Frecuencia absoluta acumulada
fabsacum  = []

#Frecuencia relativa
frel = []

#Frecuencia relativa acumulada
frelacum = []

#marcas de clase
marcas = []

@app.route('/' ,methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        # Tomamos el archivo del input
        input = request.form.get("datos")
        # validamos si no esta vacio
        if not input:
            print("\nNo hay datos\n")
            return render_template('index.html')

        
        valores_separados = input.split()  # Dividir los valores por espacios

        for valor_str in valores_separados:
            try:
                valor_numerico = float(valor_str)
                data.append(valor_numerico)
            except ValueError:
                return render_template('index.html')
            
        MinValue = min(data)
        print(MinValue)
        Total = len(data)
        print(Total)
        r =  max(data)-min(data)
        print(r)

        #Redondear al entero mas cercano
        linferior = floor(MinValue)
        Total = len(data)

                
        # Ciclo que recorre los intervalos
        intervalos = 1 + (3.322 * log10(Total))
        print(intervalos)
        k = round(intervalos)
        print(k)
        lon = r / k
        print(lon)

        for i in range(1, round(intervalos)+1):

            # Calculando el limite superior y redondeandolo a su próximo más cercano

            lsuperior = ceil(linferior + lon)

            # Añadiendo a la lista las marcas de clase

            marcas.append((linferior + lsuperior) / 2)

            # Añadiendo a la lista las frecuencias absolutas
            fabs.append(freqabs (data, linferior, lsuperior))

            # Añadiendo a la lista Las frecuencias absolutas acumuladas 
            fabsacum.append(freqabsacum(fabs))

            #Añadiendo a la lista Las frecuencias relativas

            frel.append(freqrel(fabs))

            # Añadiendo a la lista las frecuencias relativas acumuladas 
            frelacum.append(freqrel(fabsacum))

            #Añadiendole valores a la tabla

            table.loc[i] = [i,f"[{linferior}, {lsuperior})", (linferior + lsuperior) / 2, freqabs(data, linferior, lsuperior), freqabsacum(fabs), freqrel(fabs), freqrel(fabsacum) ]

            #Modificando en valor del límite inferior en cada iteración

            linferior = lsuperior

            
        print(table)
        return render_template('result.html',table=table)

        



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


# Funcion para contar numeros en un rango (Frecuencia absoluta)

def freqabs(lista, linferior, lsuperior):
    # Filtrar elementos en la lista que coincidan en los intervalos Y contarlos
    return len([x for x in lista if x >= linferior and x <= lsuperior])

# Funcion para acumular freq absolutas

def freqabsacum(lista):
    acumulado = 0
    # Recorriendo la lista de freq absolutas
    for i in lista:
        # Sumando la freq anterior
        acumulado = acumulado + i
    # Retornando el valor 
    return acumulado

# Funcion que calcula la frecuencia relativa / frecuencia relativa acumulada

def freqrel(lista):
    # Recorriendo la lista de freq absolutas / absoluta acumulada
    for i in lista: 
        # Calculando la frecuencia relativa
        freqactual = i / 40
    # Retornando el valor
    return freqactual

# Funcion para calcular la freq porcentual / freq porcentual acumulada
def freqpor(lista):

    # Recorriendo la lista de freq relativas / freq relativa acumulada
    for i in lista:
        # Calculando la frecuencia porcentual
        freqactual = i * 100
    # Retornando el valor
    return freqactual




if __name__ == '__main__':
    app.debug = True
    app.run()
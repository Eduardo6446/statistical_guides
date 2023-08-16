
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

@app.route('/' ,methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return render_template("index.html")
    else:
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
        # Tomamos el archivo del input
        input = request.form.get("datos")
        # validamos si no esta vacio
        if not input:
            print("\nNo hay datos\n")
            return render_template('index.html')
        
        for filename in os.listdir('static'):
            if filename.endswith(".png"):
                os.remove(os.path.join('static', filename))

        
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
        images = {}
    


        images = {
            'polygon': generate_plot(fabsacum, 'polygon',k),
            'histogram': generate_plot(data, 'histogram',k),
            'ojiva':generate_plot(fabsacum,'ojiva',k),
            'bar': generate_plot(data, 'bar', k),
            #'bar3d': generate_plot(data, 'bar3d', k),
            'pie': generate_plot(fabs, 'pie', k),
            'box':generate_plot(data, 'box',k)
        }

        #guia 2
        mean = np.mean(data)#media aritmetica
        median = np.median(data)#mediana
        variance = np.var(data, ddof=1)  # Usar ddof=1 para calcular la varianza muestral
        std_deviation = np.std(data, ddof=1)  # Usar ddof=1 para calcular la desviación estándar muestral

        q1 = np.percentile(data, 25)#primer cuartil
        q3 = np.percentile(data, 75)# tercer cuartil
        interquartile_range = q3 - q1
        #data.sort()  # Ordenar en forma creciente
        sorted_data = sorted(data)  # Obtener una nueva lista ordenada


        list1 = [

            ("Media Aritmética", mean),
            ("Mediana", median),
            ("Varianza Muestral", variance),
            ("Desviación Estándar Muestral", std_deviation),
            ("Primer Cuartil", q1),
            ("Tercer Cuartil", q3),
            ("Rango Intercuartil", interquartile_range),
        ]

        list2 = [
            ("Total de datos", Total),
            ("Valor minimo", min(data)),
            ("Valor maximo", max(data)),
            ("Rango", r),
        ]
            
        print(table)
        return render_template('result.html',table=table, images=images,list=list1,list2 = list2,sort_list = sorted_data)

        
def generate_plot(data, plot_type,inter):
    plt.figure(figsize=(8, 6))
    
    if plot_type == 'polygon':
        plt.plot(data, marker='o', linestyle='-', color='b')
        plt.title('Polígono de Frecuencia')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')
    elif plot_type == 'histogram':
        plt.hist(data, inter, edgecolor='black', alpha=0.7)
        plt.title('Histograma')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')
    elif plot_type == 'ojiva':
        cumulative_data = np.cumsum(data)
        print(cumulative_data)
        plt.plot(np.sort(data), np.linspace(0, len(data), len(data), endpoint=False), marker='o', linestyle='-', color='g')
        plt.title('Gráfico de Ojiva')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia acumulada')
    elif plot_type == 'bar':
        # Gráfico de Barras Normal
        plt.bar(np.arange(len(data)), data, align='center', alpha=0.7)
        plt.title('Gráfico de Barras Normal')
        plt.xlabel('Índice')
        plt.ylabel('Valor')
    elif plot_type == 'bar3d':
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        x_pos = np.arange(len(data))
        y_pos = np.arange(len(data))
        x_pos, y_pos = np.meshgrid(x_pos, y_pos)
        x_pos = x_pos.flatten()
        y_pos = y_pos.flatten()
        z_pos = np.zeros_like(x_pos)
        dx = dy = 0.75
        dz = data
        
        ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, shade=True)
        plt.title('Gráfico de Barras 3D')
        plt.xlabel('Índice')
        plt.ylabel('Índice')
    elif plot_type == 'pie':
        plt.pie(data, labels=range(len(data)), autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Gráfico de Pastel')
    elif plot_type == 'box':
        plt.boxplot(data)
        plt.title('Diagrama de Caja')
        plt.ylabel('Valor')
    elif plot_type == '':
        print("")


    
    image_path = f'static/{plot_type}.png'  # Ruta donde se guardará la imagen
    plt.savefig(image_path, format='png')
    
    plt.close()
    
    
    return image_path


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
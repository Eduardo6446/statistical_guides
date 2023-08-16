import matplotlib
matplotlib.use('Agg')  # Establecer el backend antes de importar pyplot

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

#Se crea un dataframe(estructura bidimensional) para asignar los datos
table = pd.DataFrame(columns=[
    'Numero',
    'Clase',
    'Marcas de clase',
    'Frecuencia absoluta',
    'Frecuencia absoluta acumulada',
    'Frecuencia relativa',
    'Frecuencia relativa acumulada',
])

@app.route('/' ,methods=["GET", "POST"])#Pagina Principal con sus metodos
def index():

    if request.method == "GET":
        return render_template("index.html")#Carga la pagina principal
    else:
        #Asignamos las listas, estas estaran al inicio del POST para limpiar sus datos cada refresco de pagina
        data = [] #Este contendrá los datos proporcionados por el usuario
        fabs  = [] #Frecuencia absoluta
        fabsacum  = [] #Frecuencia absoluta acumulada
        frel = [] #Frecuencia relativa
        frelacum = [] #Frecuencia relativa acumulada
        marcas = [] #marcas de clase


        input = request.form.get("datos") #Tomamos los datos proporcionados por el usuario

        if not input: # validamos si no esta vacio
            print("\nNo hay datos\n")
            return render_template('index.html')
        
        for filename in os.listdir('static'): #Este ciclo revisa si hay alguna imagen en static, si la hay la eliminará
            if filename.endswith(".png"):
                os.remove(os.path.join('static', filename))

        
        valores_separados = input.split() #Dividir los valores por espacios

        for valor_str in valores_separados: #Añadimos los datos a la lista data
            try:
                valor_numerico = float(valor_str)
                data.append(valor_numerico)
            except ValueError: #Si hay algun error devolvemos a la pagina principal
                return render_template('index.html')
            
        #Formulas utilizadas
        Total = len(data) #Este toma el total de datos que hay en la lista
        MaxValue = max(data) #Obtiene el dato mas alto
        MinValue = min(data) #Obtiene el dato mas bajo
        r =  max(data)-min(data) #Rango
        linferior = floor(MinValue) #Redondear al entero mas cercano para tomar el limite inferior
        intervalos = 1 + (3.322 * log10(Total)) #Formula para sacar los intervalos
        k = round(intervalos) #Redondeamos el dato
        lon = r / k #Longitud o amplitud
        
        #Formulas de la guia2
        mean = np.mean(data) #media aritmetica
        median = np.median(data) #mediana
        variance = np.var(data, ddof=1)  #Usar ddof=1 para calcular la varianza muestral
        std_deviation = np.std(data, ddof=1)  #Usar ddof=1 para calcular la desviación estándar muestral

        q1 = np.percentile(data, 25) #primer cuartil
        q3 = np.percentile(data, 75) #tercer cuartil
        interquartile_range = q3 - q1
        #data.sort()  # Ordenar en forma creciente
        sorted_data = sorted(data)  #Obtener una nueva lista ordenada
        
        for i in range(1, round(intervalos)+1): #Ciclo que recorre los intervalos

            lsuperior = ceil(linferior + lon) #Calculando el limite superior y redondeandolo a su próximo más cercano
            marcas.append((linferior + lsuperior) / 2) #Añadiendo a la lista las marcas de clase
            fabs.append(freqabs (data, linferior, lsuperior)) #Añadiendo a la lista las frecuencias absolutas 
            fabsacum.append(freqabsacum(fabs)) #Añadiendo a la lista Las frecuencias absolutas acumuladas
            frel.append(freqrel(fabs,Total)) #Añadiendo a la lista Las frecuencias relativas 
            frelacum.append(freqrel(fabsacum,Total)) #Añadiendo a la lista las frecuencias relativas acumuladas

            table.loc[i] = [i,f"[{linferior}, {lsuperior})", (linferior + lsuperior) / 2, freqabs(data, linferior, lsuperior), freqabsacum(fabs), freqrel(fabs,Total), freqrel(fabsacum,Total)] #Añadiendole valores a la tabla

            linferior = lsuperior#Modificando en valor del límite inferior en cada iteración
        
        images = {} #Asignamos la lista de imagenes
    
        images = { #Creamos las imagenes mediante la funcion generate_plot
            'polygon': generate_plot(fabsacum, 'polygon',k), #Poligono de frecuencia
            'histogram': generate_plot(data, 'histogram',k), #Historigrama
            'ojiva':generate_plot(fabsacum,'ojiva',k), #Grafico de ojiva
            'bar': generate_plot(data, 'bar', k), #Grafico de barras
            'pie': generate_plot(fabs, 'pie', k), #Grafico Pastel
            'box':generate_plot(data, 'box',k) #Grafico de caja
        }

        #Se divivio en dos para mejor orden
        list1 = [#diccionario de la guia 2

            ("Media Aritmética", mean),
            ("Mediana", median),
            ("Varianza Muestral", variance),
            ("Desviación Estándar Muestral", std_deviation),
            ("Primer Cuartil", q1),
            ("Tercer Cuartil", q3),
            ("Rango Intercuartil", interquartile_range),
        ]

        list2 = [ #diccionario de la guia 1
            ("Total de datos", Total),
            ("Valor minimo", min(data)),
            ("Valor maximo", max(data)),
            ("Rango", r),
        ]            
        return render_template('result.html',table=table, images=images,list=list1,list2 = list2,sort_list = sorted_data)

        
def generate_plot(data, plot_type,inter): #Esta funcion genera los graficos
    plt.figure(figsize=(8, 6)) #Tamaño de la imagen
    
    if plot_type == 'polygon': #Poligono de frecuencia
        plt.plot(data, marker='o', linestyle='-', color='b')
        plt.title('Polígono de Frecuencia')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')

    elif plot_type == 'histogram': #Historigrama
        plt.hist(data, inter, edgecolor='black', alpha=0.7)
        plt.title('Histograma')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')

    elif plot_type == 'ojiva': #Ojiva
        cumulative_data = np.cumsum(data)
        print(cumulative_data)
        plt.plot(np.sort(data), np.linspace(0, len(data), len(data), endpoint=False), marker='o', linestyle='-', color='g')
        plt.title('Gráfico de Ojiva')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia acumulada')

    elif plot_type == 'bar': #Gráfico de Barras Normal
        plt.bar(np.arange(len(data)), data, align='center', alpha=0.7)
        plt.title('Gráfico de Barras Normal')
        plt.xlabel('Índice')
        plt.ylabel('Valor')

    elif plot_type == 'bar3d': #Gráfico de Barras Normal
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

    elif plot_type == 'pie': #Grafico pastel
        plt.pie(data, labels=range(len(data)), autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Gráfico de Pastel')

    elif plot_type == 'box': #Grafico de caja
        plt.boxplot(data)
        plt.title('Diagrama de Caja')
        plt.ylabel('Valor')
    
    image_path = f'static/{plot_type}.png' #Ruta donde se guardará la imagen
    plt.savefig(image_path, format='png') #Guardamos la figura con el formato png
    plt.close() #Cerramos
    
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


def freqrel(lista,total): #Funcion que calcula la frecuencia relativa / frecuencia relativa acumulada

    for i in lista:#Recorriendo la lista de freq absolutas / absoluta acumulada
        freqactual = i / total #Calculando la frecuencia relativa
    # Retornando el valor
    return freqactual

def freqpor(lista): #Funcion para calcular la freq porcentual / freq porcentual acumulada

    for i in lista: #Recorriendo la lista de freq relativas / freq relativa acumulada
        freqactual = i * 100 #Calculando la frecuencia porcentual
    # Retornando el valor
    return freqactual


if __name__ == '__main__':
    app.debug = True
    app.run()
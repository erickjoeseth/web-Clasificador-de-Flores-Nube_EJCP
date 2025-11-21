import os
import sys
import tensorflow as tf
import numpy as np
import json
import base64
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing import image

# --- CONFIGURACIÓN ---
# Desactivamos logs molestos de TF
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Rutas
RUTA_MODELO = 'mi_modelo_flores.h5'
RUTA_ETIQUETAS = 'labels.json'

# Traductor
TRADUCTOR = {
    "daisy": "Margarita",
    "dandelion": "Diente de león",
    "roses": "Rosa",
    "sunflowers": "Girasol",
    "tulips": "Tulipán"
}

# --- INICIO FLASK ---
app = Flask(__name__)
# Configuración de subida
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}
# Crear carpeta si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Variables globales
modelo = None
etiquetas = None

# --- FUNCIONES AUXILIARES ---

def cargar_modelo():
    global modelo, etiquetas
    if modelo is None:
        if not os.path.exists(RUTA_MODELO) or not os.path.exists(RUTA_ETIQUETAS):
            print("ERROR CRÍTICO: No se encuentran el modelo o las etiquetas.")
            return False
        print("Cargando modelo...")
        modelo = tf.keras.models.load_model(RUTA_MODELO)
        with open(RUTA_ETIQUETAS, 'r') as archivo:
            etiquetas = json.load(archivo)
        print("¡Modelo cargado!")
    return True

def archivo_permitido(nombre_archivo):
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def analizar_imagen_logica(ruta_imagen):
    # Preprocesamiento
    imagen_cargada = image.load_img(ruta_imagen, target_size=(224, 224))
    arreglo_imagen = image.img_to_array(imagen_cargada)
    arreglo_imagen = arreglo_imagen / 255.0
    arreglo_imagen = np.expand_dims(arreglo_imagen, axis=0)

    # Predicción
    predicciones = modelo.predict(arreglo_imagen, verbose=0)
    
    # Decodificación
    indice_predicho = np.argmax(predicciones[0])
    confianza = float(predicciones[0][indice_predicho])
    
    # Obtener Top 3
    indices_ordenados = np.argsort(predicciones[0])[::-1]
    top_predicciones = []
    for idx in indices_ordenados[:3]:
        nombre_ingles = etiquetas[str(idx)]
        nombre_espanol = TRADUCTOR.get(nombre_ingles, nombre_ingles)
        top_predicciones.append({
            "nombre": nombre_espanol.capitalize(),
            "confianza": float(predicciones[0][idx]) * 100
        })

    # Resultado Principal
    nombre_ingles_main = etiquetas[str(indice_predicho)]
    nombre_espanol_main = TRADUCTOR.get(nombre_ingles_main, nombre_ingles_main)

    return {
        "nombre_flor": nombre_espanol_main.capitalize(),
        "confianza": confianza * 100,
        "confianza_suficiente": confianza > 0.5,
        "top_predicciones": top_predicciones
    }

# --- RUTAS DE LA WEB ---

@app.route('/')
def index():
    # Nos aseguramos de cargar el modelo al entrar
    cargar_modelo()
    return render_template('index.html')

@app.route('/clasificar', methods=['POST'])
def clasificar():
    # Asegurar carga del modelo
    if modelo is None:
        if not cargar_modelo():
            return jsonify({'error': 'El modelo no está disponible en el servidor'}), 500

    if 'imagen' not in request.files:
        return jsonify({'error': 'No se recibió imagen'}), 400
    
    archivo = request.files['imagen']
    
    if archivo.filename == '' or not archivo_permitido(archivo.filename):
        return jsonify({'error': 'Archivo no válido'}), 400

    try:
        # Guardar y Procesar
        nombre_seguro = secure_filename(archivo.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
        archivo.save(ruta_completa)

        # Analizar
        resultado = analizar_imagen_logica(ruta_completa)

        # Convertir imagen a Base64 para devolverla al frontend sin recargar
        with open(ruta_completa, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        resultado['imagen_base64'] = encoded_string
        
        # Limpiar archivo temporal
        os.remove(ruta_completa)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    # Cargar modelo antes de iniciar servidor
    cargar_modelo()
    # host='0.0.0.0' es OBLIGATORIO para Render
    app.run(host='0.0.0.0', port=5000)
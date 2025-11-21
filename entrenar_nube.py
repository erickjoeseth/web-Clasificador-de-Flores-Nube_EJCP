import os
# Solución para el error de protobuf con tensorflow-datasets
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import tensorflow as tf
import tensorflow_datasets as tfds  # ¡La nueva biblioteca!
import json

# --- Configuración ---
TAMANO_IMAGEN = (224, 224)
TAMANO_LOTE = 16
EPOCAS = 10
# ---------------------

print("Iniciando el script de entrenamiento (Versión 3: Nube)...")

# ===================================================================
# 1. Cargar Datos (¡LA PARTE NUEVA!)
# ===================================================================
print("Descargando y preparando el dataset 'tf_flowers' de la nube...")

# tfds.load descarga y prepara el dataset.
# Dividimos el 100% de los datos en 80% para entrenar y 20% para validar.
(datos_entrenamiento, datos_validacion), informacion = tfds.load(
    'tf_flowers',
    split=['train[:80%]', 'train[80%:]'], # Divide el set de 'train'
    as_supervised=True, # Devuelve (imagen, etiqueta)
    with_info=True
)

# 2. Guardar las etiquetas (labels)
# Obtenemos los nombres de las 5 clases del dataset
etiquetas = {i: name for i, name in enumerate(informacion.features['label'].names)}
num_clases = informacion.features['label'].num_classes

with open('labels.json', 'w') as archivo:
    json.dump(etiquetas, archivo)

print(f"Dataset 'tf_flowers' cargado. Detectó {num_clases} clases: {list(etiquetas.values())}")

# 3. Preprocesar las imágenes (Necesario para los datasets de TFDS)
# Esta función ajustará el tamaño y normalizará cada imagen
def preprocesar_imagen(imagen, etiqueta):
    imagen = tf.image.resize(imagen, TAMANO_IMAGEN)
    imagen = tf.cast(imagen, tf.float32) / 255.0 # Normalizar
    return imagen, etiqueta

# Aplicamos la función a todos los datos y preparamos los lotes
datos_entrenamiento = datos_entrenamiento.map(preprocesar_imagen).shuffle(100).batch(TAMANO_LOTE).prefetch(tf.data.AUTOTUNE)
datos_validacion = datos_validacion.map(preprocesar_imagen).batch(TAMANO_LOTE).prefetch(tf.data.AUTOTUNE)

# ===================================================================

# 4. Cargar el Modelo Base (Transfer Learning)
modelo_base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
modelo_base.trainable = False

# 5. Construir nuestro "Cerebro" (Modelo final)
modelo = tf.keras.Sequential([
    modelo_base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(num_clases, activation='softmax') # num_clases será 5
])

# 6. Compilar el modelo
# ¡Importante! Usamos 'sparse_categorical_crossentropy' porque las etiquetas
# de TFDS son números (0, 1, 2...) no arrays [0,0,1,0,0]
modelo.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 7. Entrenar el Modelo
print(f"\nIniciando entrenamiento por {EPOCAS} épocas...")
historial = modelo.fit(
    datos_entrenamiento,  # Usamos el dataset de la nube
    epochs=EPOCAS,
    validation_data=datos_validacion # Usamos el dataset de validación de la nube
)

# 8. Guardar el Modelo Entrenado
modelo.save('mi_modelo_flores.h5')
print("\n¡Entrenamiento completo! Modelo guardado como 'mi_modelo_flores.h5'")
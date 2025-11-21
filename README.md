# Clasificador de Flores con IA - Versión Web Flask

Sistema de clasificación de flores usando TensorFlow y Flask con una interfaz web interactiva.

## 🌺 Características

- Clasificación de 5 tipos de flores: Margarita, Diente de león, Rosa, Girasol y Tulipán
- Interfaz web moderna y responsiva
- Drag & Drop para subir imágenes
- Visualización de resultados con top 3 predicciones
- Modelo basado en MobileNetV2 con Transfer Learning

## 📋 Requisitos

- Python 3.8 o superior
- TensorFlow 2.10 o superior
- Flask 2.3 o superior

## 🚀 Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Entrena el modelo (si aún no lo has hecho):
```bash
python entrenar_nube.py
```

Esto descargará el dataset de TensorFlow, entrenará el modelo y guardará:
- `mi_modelo_flores.h5` - El modelo entrenado
- `labels.json` - Las etiquetas de las clases

## 🎯 Uso

### Ejecutar la aplicación web Flask:

```bash
python appv3.py
```

Luego abre tu navegador en: `http://localhost:5000`

La aplicación iniciará automáticamente el servidor Flask con la interfaz web.

## 📁 Estructura del Proyecto

```
.
├── appv3.py              # Aplicación Flask principal (único archivo)
├── entrenar_nube.py      # Script de entrenamiento
├── requirements.txt      # Dependencias
├── templates/
│   └── index.html        # Interfaz web
├── static/
│   ├── css/
│   │   └── estilos.css   # Estilos
│   └── js/
│       └── script.js     # JavaScript interactivo
└── uploads/              # Carpeta temporal para imágenes (se crea automáticamente)
```

## 🎨 Características de la Interfaz Web

- **Drag & Drop**: Arrastra imágenes directamente al área de carga
- **Vista previa**: Visualiza la imagen antes de analizarla
- **Resultados animados**: Barras de confianza y animaciones suaves
- **Top 3 predicciones**: Muestra las 3 mejores clasificaciones
- **Diseño responsivo**: Funciona en móviles y tablets
- **Feedback visual**: Indicadores de carga y mensajes de error claros

## 🔧 Notas Técnicas

- El modelo se carga automáticamente al iniciar la aplicación Flask
- Las imágenes se procesan temporalmente y se eliminan después del análisis
- Tamaño máximo de archivo: 16MB
- Formatos soportados: JPG, PNG, JPEG, WEBP

## 📝 Notas

- `appv3.py` es el único archivo de la aplicación Flask. Contiene tanto las funciones de análisis como las rutas de Flask.
- La función `analizar_imagen_web()` se usa para la interfaz web, mientras que `analizar_imagen()` está disponible para uso programático.

## 🐛 Solución de Problemas

Si el modelo no se carga:
1. Asegúrate de haber ejecutado `entrenar_nube.py` primero
2. Verifica que existan los archivos `mi_modelo_flores.h5` y `labels.json`
3. Revisa los mensajes de error en la consola

## 📄 Licencia

Este proyecto es de uso educativo.


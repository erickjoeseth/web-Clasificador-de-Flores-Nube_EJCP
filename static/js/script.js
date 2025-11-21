// Variables globales
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const btnNewImage = document.getElementById('btnNewImage');
const btnReanalyze = document.getElementById('btnReanalyze');

let selectedFile = null;

// Event listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
removeBtn.addEventListener('click', removeImage);
analyzeBtn.addEventListener('click', analyzeImage);
btnNewImage.addEventListener('click', uploadNewImage);
btnReanalyze.addEventListener('click', reanalyzeImage);

// Funciones de drag and drop
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// Manejo de selección de archivo
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

// Procesar archivo seleccionado
function processFile(file) {
    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
        showError('Por favor, selecciona un archivo de imagen válido.');
        return;
    }
    
    // Validar tamaño (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('El archivo es demasiado grande. Máximo 16MB.');
        return;
    }
    
    selectedFile = file;
    
    // Mostrar vista previa
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
        hideError();
    };
    reader.readAsDataURL(file);
}

// Remover imagen
function removeImage() {
    selectedFile = null;
    fileInput.value = '';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    hideError();
}

// Analizar imagen
async function analyzeImage() {
    if (!selectedFile) {
        showError('Por favor, selecciona una imagen primero.');
        return;
    }
    
    // Mostrar estado de carga
    analyzeBtn.disabled = true;
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    btnText.textContent = 'Analizando...';
    btnLoader.style.display = 'inline-block';
    
    hideError();
    
    try {
        // Crear FormData
        const formData = new FormData();
        formData.append('imagen', selectedFile);
        
        // Enviar petición
        const response = await fetch('/clasificar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al procesar la imagen');
        }
        
        // Mostrar resultados
        displayResults(data);
        
    } catch (error) {
        showError(error.message || 'Error al analizar la imagen. Por favor, intenta de nuevo.');
    } finally {
        // Restaurar botón
        analyzeBtn.disabled = false;
        btnText.textContent = 'Analizar Imagen';
        btnLoader.style.display = 'none';
    }
}

// Mostrar resultados
function displayResults(data) {
    // Mostrar imagen analizada
    const resultImage = document.getElementById('resultImage');
    resultImage.src = `data:${data.tipo_imagen};base64,${data.imagen_base64}`;
    
    // Mostrar nombre de la flor
    const flowerName = document.getElementById('flowerName');
    flowerName.textContent = data.nombre_flor;
    
    // Mostrar confianza
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    const confidence = data.confianza.toFixed(1);
    
    confidenceFill.style.width = `${confidence}%`;
    confidenceFill.textContent = `${confidence}%`;
    confidenceText.textContent = `Confianza: ${confidence}%`;
    
    // Mostrar alerta si la confianza es baja
    const resultAlert = document.getElementById('resultAlert');
    if (!data.confianza_suficiente) {
        resultAlert.style.display = 'block';
    } else {
        resultAlert.style.display = 'none';
    }
    
    // Mostrar top predicciones
    displayTopPredictions(data.top_predicciones);
    
    // Mostrar sección de resultados
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Mostrar top predicciones
function displayTopPredictions(predictions) {
    const predictionsList = document.getElementById('predictionsList');
    predictionsList.innerHTML = '';
    
    predictions.forEach((pred, index) => {
        const item = document.createElement('div');
        item.className = `prediction-item ${index === 0 ? 'top' : ''}`;
        
        const name = document.createElement('span');
        name.className = 'prediction-name';
        name.textContent = `${index + 1}. ${pred.nombre}`;
        
        const confidence = document.createElement('span');
        confidence.className = 'prediction-confidence';
        confidence.textContent = `${pred.confianza.toFixed(1)}%`;
        
        item.appendChild(name);
        item.appendChild(confidence);
        predictionsList.appendChild(item);
    });
}

// Mostrar error
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Ocultar error
function hideError() {
    errorMessage.style.display = 'none';
}

// Subir nueva imagen
function uploadNewImage() {
    // Limpiar todo
    selectedFile = null;
    fileInput.value = '';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    hideError();
    
    // Scroll al área de carga
    uploadArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Volver a analizar la misma imagen
function reanalyzeImage() {
    if (selectedFile) {
        // Ocultar resultados y mostrar solo la vista previa
        resultsSection.style.display = 'none';
        previewSection.style.display = 'block';
        
        // Scroll a la vista previa
        previewSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Analizar automáticamente
        analyzeImage();
    } else {
        showError('No hay imagen para analizar. Por favor, sube una imagen primero.');
    }
}


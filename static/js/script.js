document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const imageInput = document.getElementById('image-input');
    const originalImg = document.getElementById('original-img');
    const outputImg = document.getElementById('output-img');
    const originalPlaceholder = document.querySelector('#original-wrapper .placeholder-text');
    const outputPlaceholder = document.querySelector('#output-wrapper .placeholder-text');
    
    const hdBtn = document.getElementById('hd-btn');
    const editBtn = document.getElementById('edit-btn');
    const promptInput = document.getElementById('prompt-input');
    const downloadBtn = document.getElementById('download-btn');
    const loadingSpinner = document.getElementById('loading-spinner');

    let currentFile = null;

    // 1. Click to trigger file input
    dropZone.addEventListener('click', () => {
        imageInput.click();
    });

    // 2. File Selection Handler
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // 3. Drag and Drop Handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#3b82f6';
        dropZone.style.background = '#f0f9ff';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#cbd5e1';
        dropZone.style.background = '#ffffff';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#cbd5e1';
        dropZone.style.background = '#ffffff';
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            alert('Please select a valid image file!');
            return;
        }

        currentFile = file;

        // Preview Original Image
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImg.src = e.target.result;
            originalImg.classList.remove('hidden');
            if (originalPlaceholder) originalPlaceholder.classList.add('hidden');
        };
        reader.readAsDataURL(file);

        // Enable Buttons and Inputs
        hdBtn.disabled = false;
        editBtn.disabled = false;
        promptInput.disabled = false;
    }

    // 4. Make HD Button Event
    hdBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        showLoading('Enhancing image quality...');
        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/api/enhance-hd', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                showResult(data.result_url);
            } else {
                alert('Error: ' + data.error);
                hideLoading();
            }
        } catch (error) {
            alert('Something went wrong!');
            hideLoading();
        }
    });

    // 5. Apply AI Edit Button Event
    editBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        if (!currentFile || !prompt) {
            alert('Please enter a prompt first!');
            return;
        }

        showLoading('Applying AI edit...');
        const formData = new FormData();
        formData.append('image', currentFile);
        formData.append('prompt', prompt);

        try {
            const response = await fetch('/api/edit-text', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                showResult(data.result_url);
            } else {
                alert('Error: ' + data.error);
                hideLoading();
            }
        } catch (error) {
            alert('Something went wrong!');
            hideLoading();
        }
    });

    function showLoading(text) {
        outputImg.classList.add('hidden');
        if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        document.getElementById('loading-text').innerText = text;
        downloadBtn.classList.add('hidden');
    }

    function hideLoading() {
        loadingSpinner.classList.add('hidden');
    }

    function showResult(url) {
        hideLoading();
        outputImg.src = url;
        outputImg.classList.remove('hidden');
        downloadBtn.href = url;
        downloadBtn.classList.remove('hidden');
    }
});
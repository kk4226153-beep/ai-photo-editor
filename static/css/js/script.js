document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const imageInput = document.getElementById('image-input');
    const originalPreview = document.getElementById('original-preview');
    const origPlaceholder = document.getElementById('orig-placeholder');
    const resultPreview = document.getElementById('result-preview');
    const resPlaceholder = document.getElementById('res-placeholder');
    const loader = document.getElementById('loader');
    
    const btnHd = document.getElementById('btn-hd');
    const btnEdit = document.getElementById('btn-edit');
    const promptInput = document.getElementById('prompt-input');
    const downloadBtn = document.getElementById('download-btn');

    let selectedFile = null;

    // Upload box click event
    dropZone.addEventListener('click', () => imageInput.click());

    // File selection
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => e.preventDefault());
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Sirf image files (PNG/JPG) upload karein!');
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            originalPreview.src = e.target.result;
            originalPreview.hidden = false;
            origPlaceholder.hidden = true;
            btnHd.disabled = false;
            btnEdit.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    async function processAIRequest(endpoint, formData) {
        loader.hidden = false;
        resultPreview.hidden = true;
        resPlaceholder.hidden = true;
        downloadBtn.hidden = true;
        btnHd.disabled = true;
        btnEdit.disabled = true;

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                resultPreview.src = data.result_url;
                resultPreview.hidden = false;
                downloadBtn.href = data.result_url;
                downloadBtn.hidden = false;
            } else {
                alert('Error: ' + (data.error || 'AI Process fail ho gaya'));
                resPlaceholder.hidden = false;
            }
        } catch (err) {
            alert('Network / Server Error');
            resPlaceholder.hidden = false;
        } finally {
            loader.hidden = true;
            btnHd.disabled = false;
            btnEdit.disabled = false;
        }
    }

    // HD Quality Button
    btnHd.addEventListener('click', () => {
        if (!selectedFile) return;
        const formData = new FormData();
        formData.append('image', selectedFile);
        processAIRequest('/api/enhance-hd', formData);
    });

    // Text Edit Button
    btnEdit.addEventListener('click', () => {
        const prompt = promptInput.value.trim();
        if (!selectedFile || !prompt) {
            alert('Pehle image upload karein aur text prompt likhein!');
            return;
        }
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('prompt', prompt);
        processAIRequest('/api/edit-text', formData);
    });
});
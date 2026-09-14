// frontend/js/app.js

document.addEventListener("DOMContentLoaded", () => {
    // --- 1. UI Animations & Scroll Observer ---
    const revealElements = document.querySelectorAll('.reveal');
    
    const revealOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // Unobserve once animated in to keep it visible
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);

    revealElements.forEach(el => revealOnScroll.observe(el));

    // --- 2. DOM Elements Selection ---
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");
    const errorMsg = document.getElementById("errorMsg");
    const resetBtn = document.getElementById("resetBtn");
    
    const uploadSection = document.getElementById("uploadSection");
    const loadingState = document.getElementById("loadingState");
    const resultSection = document.getElementById("resultSection");
    
    const originalPreview = document.getElementById("originalPreview");
    const syntheticPreview = document.getElementById("syntheticPreview");
    const upcycleTitle = document.getElementById("upcycleTitle");
    const detectedMaterial = document.getElementById("detectedMaterial");
    const estimatedTime = document.getElementById("estimatedTime");
    const difficultyLevel = document.getElementById("difficultyLevel");
    const toolsList = document.getElementById("toolsList");
    const stepsContainer = document.getElementById("stepsContainer");

    const API_URL = "http://localhost:8000/api/v1/analyze";

    // --- 3. Drag and Drop Interaction Logic ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add("dragover"), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove("dragover"), false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFile(files[0]);
    });

    browseBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", function() {
        if (this.files.length) handleFile(this.files[0]);
    });

    resetBtn.addEventListener("click", resetUI);

    // --- 4. File Handling & API Integration ---
    function handleFile(file) {
        errorMsg.classList.add("hidden");
        
        // Front-end validation
        if (!file.type.startsWith("image/")) {
            showError("Please upload a valid image file (PNG, JPG, WEBP).");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showError("File size exceeds 10MB limit.");
            return;
        }

        // Generate a local preview of the uploaded image instantly
        const reader = new FileReader();
        reader.onload = (e) => {
            originalPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);

        processImageWithAI(file);
    }

    async function processImageWithAI(file) {
        // Transition UI to loading state
        uploadSection.classList.add("hidden");
        loadingState.classList.remove("hidden");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to process image through AI pipeline.");
            }

            const data = await response.json();
            renderResults(data);
            
        } catch (error) {
            resetUI();
            showError(error.message);
        }
    }

    // --- 5. Dynamic Data Rendering ---
    function renderResults(data) {
        loadingState.classList.add("hidden");
        resultSection.classList.remove("hidden");

        // Update Text and Metadata Badges
        upcycleTitle.textContent = data.upcycling_title;
        detectedMaterial.textContent = `${data.original_category} (${data.confidence}%)`;
        estimatedTime.textContent = data.estimated_time;
        difficultyLevel.textContent = data.difficulty;
        
        // Render Generative AI Concept Image
        syntheticPreview.src = data.synthetic_image_base64;

        // Render Required Tools
        toolsList.innerHTML = "";
        data.tools_needed.forEach(tool => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-check" style="color: var(--primary); margin-right: 8px;"></i> ${tool}`;
            toolsList.appendChild(li);
        });

        // Render Step-by-Step Instructions
        stepsContainer.innerHTML = "";
        data.instructions.forEach(step => {
            const stepHtml = `
                <div class="step-card">
                    <div class="step-header">
                        <span class="step-num">${step.step_number}</span>
                        <h4>${step.title}</h4>
                    </div>
                    <p style="padding-left: calc(28px + 1rem); color: var(--text-muted); font-size: 0.95rem;">
                        ${step.description}
                    </p>
                </div>
            `;
            stepsContainer.insertAdjacentHTML("beforeend", stepHtml);
        });

        // Automatically scroll to the results for better UX
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showError(message) {
        errorMsg.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${message}`;
        errorMsg.classList.remove("hidden");
    }

    function resetUI() {
        fileInput.value = "";
        uploadSection.classList.remove("hidden");
        resultSection.classList.add("hidden");
        loadingState.classList.add("hidden");
        errorMsg.classList.add("hidden");
        
        // Scroll back to the upload area
        document.getElementById("hero").scrollIntoView({ behavior: 'smooth' });
    }
});
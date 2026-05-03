// Barcode capturing configs
let barcodeInput = "";
let barcodeTimeout = null;
const BARCODE_DELAY = 100; // ms

// Recording state
let isRecording = false;
let mediaRecorder = null;
let recordedChunks = [];
let currentInvoice = "";
let currentStartTime = null;
let currentDurationObj = null;

// Overlay State
const canvas = document.getElementById('video-overlay');
const ctx = canvas.getContext('2d');
const video = document.getElementById('webcam-preview');
let animationFrameId;

// Access Camera
async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1920 },
                height: { ideal: 1080 },
                facingMode: "environment"
            },
            audio: false 
        });
        video.srcObject = stream;
        
        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        });
        
        video.addEventListener('play', () => {
            if (!mediaRecorder) {
                // Pass canvas stream to recorder to burn overlays
                const canvasStream = canvas.captureStream(30);
                setupMediaRecorder(canvasStream);
                drawOverlay(); // Start loop
            }
        });
    } catch (err) {
        console.error("Camera access failed", err);
        App.showToast("Cannot access camera. Please allow permissions.", "error");
    }
}

function setupMediaRecorder(stream) {
    // Try to get a high-quality mp4-compatible local format if possible, or cross-compatible webm.
    // Chrome uses webm for MediaRecorder usually, but it can be stored identically. Video codec is vp8/9
    const options = { mimeType: 'video/webm; codecs=vp9' };
    
    try {
        mediaRecorder = new MediaRecorder(stream, (MediaRecorder.isTypeSupported('video/webm; codecs=vp9') ? options : undefined));
    } catch(e) {
        mediaRecorder = new MediaRecorder(stream);
    }

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };

    mediaRecorder.onstart = () => {
        isRecording = true;
        recordedChunks = [];
        currentStartTime = new Date();
        document.getElementById('recording-status').classList.remove('hidden');
        document.getElementById('stop-instruction').classList.remove('opacity-50');
        
        // Timer update
        currentDurationObj = setInterval(() => {
            const diff = Math.floor((Date.now() - currentStartTime.getTime()) / 1000);
            const m = String(Math.floor(diff / 60)).padStart(2, '0');
            const s = String(diff % 60).padStart(2, '0');
            document.getElementById('recording-timer').innerText = `${m}:${s}`;
        }, 1000);
    };

    mediaRecorder.onstop = async () => {
        isRecording = false;
        clearInterval(currentDurationObj);
        document.getElementById('recording-status').classList.add('hidden');
        document.getElementById('stop-instruction').classList.add('opacity-50');
        
        const durationSeconds = Math.floor((Date.now() - currentStartTime.getTime()) / 1000);
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        
        await uploadVideo(blob, currentInvoice, currentStartTime, durationSeconds);
        currentInvoice = ""; // Clear invoice after upload
        App.showToast("Recording saved and uploaded.", "success");
        loadRecentVideos();
    };
}

// Upload mechanism
async function uploadVideo(blob, invoice, startTime, duration) {
    const formData = new FormData();
    // Re-pack blob as mp4 extension so we store it as requested. (Since MediaRecorder produces webm initially)
    formData.append("video", blob, `${invoice}.mp4`);
    formData.append("invoice_number", invoice);
    formData.append("timestamp_start", startTime.toISOString());
    formData.append("duration", duration.toString());
    
    try {
        const response = await fetch('/api/videos/upload', {
            method: 'POST',
            headers: App.authHeader(),
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
    } catch(err) {
        console.error(err);
        App.showToast("Error uploading video. Check connection.", "error");
    }
}

// Burn video feed and text overlay into the canvas
function drawOverlay() {
    if(!ctx) return;
    
    // Draw the actual webcam feed onto the canvas background
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Dynamically scale text based on canvas native resolution
    const scale = Math.max(canvas.height / 720, 1);
    const boxWidth = 600 * scale;
    const fontSize = 20 * scale;
    const lineSpacing = fontSize * 1.5;
    const padding = 30 * scale;
    
    // Calculate dynamic box height based on active lines
    const numLines = isRecording ? 3 : 2;
    const boxHeight = (lineSpacing * numLines) + (padding * 0.8);
    
    // Bottom left overlay box
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(padding, canvas.height - boxHeight - padding, boxWidth, boxHeight);
    
    ctx.fillStyle = 'white';
    // Align text cleanly inside the box
    ctx.textBaseline = 'top'; 
    
    // Data
    const username = localStorage.getItem('username');
    const now = new Date().toLocaleString('id-ID', { dateStyle: 'full', timeStyle: 'medium' });
    
    // Start drawing from top of the box + padding
    let currentY = canvas.height - boxHeight - padding + (padding * 0.5);
    
    if (isRecording) {
        ctx.fillStyle = '#ef4444'; // Red
        ctx.font = `bold ${fontSize}px monospace`;
        ctx.fillText(`Pesanan ${currentInvoice}`, padding * 1.5, currentY);
        currentY += lineSpacing;
    }
    
    ctx.fillStyle = 'white';
    ctx.font = `${fontSize}px monospace`;
    
    ctx.fillText(`USER : ${username}`, padding * 1.5, currentY);
    currentY += lineSpacing;
    
    ctx.fillText(`TIME : ${now}`, padding * 1.5, currentY);
    
    animationFrameId = requestAnimationFrame(drawOverlay);
}

// Keyboard input for F8 and Barcode Capture
document.addEventListener('keydown', (e) => {
    // 119 is F8 keycode, check by key directly
    if (e.key === "F8") {
        e.preventDefault();
        if (isRecording && mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        } else {
            App.showToast("Not currently recording.", "warning");
        }
        return;
    }
    
    // Ignore input if it's targeting an active element like a text box (dashboard logic might have inputs)
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
    }
    
    // Barcode scanner typically types fast and hits Enter
    if (e.key === "Enter") {
        if (barcodeInput.trim().length > 0) {
            handleBarcodeScanned(barcodeInput.trim());
        }
        barcodeInput = "";
        return;
    }

    // Capture standard typable chars for barcode
    if (e.key.length === 1) {
        barcodeInput += e.key;
        
        if(barcodeTimeout) clearTimeout(barcodeTimeout);
        barcodeTimeout = setTimeout(() => {
            // Buffer expired without finding 'Enter', discard assuming it was manual typing
            barcodeInput = "";
        }, BARCODE_DELAY);
    }
});

function startManualRecording() {
    const inputEL = document.getElementById('manual-invoice');
    const val = inputEL.value.trim();
    if(val.length > 0) {
        handleBarcodeScanned(val);
        inputEL.value = ""; // clear after starting
    } else {
        App.showToast("Silakan isi nomor invoice terlebih dahulu", "warning");
    }
}

function handleBarcodeScanned(barcode) {
    if (isRecording) {
        App.showToast("Recording already in progress. Press F8 to stop.", "error");
        return;
    }
    
    if (barcode.length < 3) return; // Prevent spurious short inputs
    
    currentInvoice = barcode;
    App.showToast(`Starting recording for ${currentInvoice}`, "success");
    
    if (mediaRecorder && mediaRecorder.state === "inactive") {
        mediaRecorder.start();
    } else {
        App.showToast("Camera not ready.", "error");
    }
}

// Fetch recent videos
async function loadRecentVideos() {
    const listContainer = document.getElementById('recent-videos-list');
    if (!listContainer) return;
    
    try {
        const input = document.getElementById('search-invoice');
        const query = input ? input.value.trim() : "";
        const url = query ? `/api/videos?invoice_number=${encodeURIComponent(query)}` : `/api/videos`;
        
        const res = await fetch(url, { headers: App.authHeader() });
        if(!res.ok) throw new Error("Failed to load");
        const payload = await res.json();
        const videos = payload.data || [];
        
        listContainer.innerHTML = '';
        if(videos.length === 0) {
            listContainer.innerHTML = '<div class="text-slate-500 text-sm text-center">Tidak ada riwayat.</div>';
            return;
        }
        
        videos.forEach(vid => {
            const d = new Date(vid.created_at + (vid.created_at.endsWith('Z') ? '' : 'Z'));
            const timeStr = d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
            
            listContainer.innerHTML += `
               <div class="bg-slate-700/50 p-3 rounded-lg border border-slate-600 flex justify-between items-center hover:bg-slate-700 transition">
                   <div>
                       <div class="text-blue-400 font-bold font-mono text-sm">${vid.invoice_number}</div>
                       <div class="text-slate-400 text-xs">${timeStr} | ${vid.duration}s</div>
                   </div>
                   <button onclick="playVideo(${vid.id})" class="text-white hover:text-emerald-400 bg-slate-800 p-2 rounded shadow">
                       <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" /></svg>
                   </button>
               </div>
            `;
        });
    } catch(e) {
        console.error(e);
        listContainer.innerHTML = '<div class="text-red-500 text-sm">Gagal memuat.</div>';
    }
}

document.getElementById('search-invoice')?.addEventListener('input', () => {
    loadRecentVideos();
});

// Modal playback
function playVideo(id) {
    const modal = document.getElementById('video-modal');
    const player = document.getElementById('modal-video-player');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    fetch(`/api/videos/play/${id}`, { headers: App.authHeader() })
        .then(res => {
            if(!res.ok) throw new Error("Load failed");
            return res.blob();
        })
        .then(blob => {
             player.src = URL.createObjectURL(blob);
             player.play();
        })
        .catch(err => {
             App.showToast("Gagal memuat video", "error");
             closeModal();
        });
}

function closeModal() {
    const modal = document.getElementById('video-modal');
    const player = document.getElementById('modal-video-player');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    player.pause();
    player.src = '';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Basic setup once DOM is ready
    setupCamera();
    loadRecentVideos();
});

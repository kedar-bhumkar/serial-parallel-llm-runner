let isRecording = false;
let jsonResponse = null;

let mediaRecorder;
let recordedChunks = [];
let audioContext;
let analyser;
let dataArray;
let bufferLength;
let canvas;
let canvasCtx;

function toggleRecording() {
    const startButton = document.querySelector('.controls button:first-child');
    const recordingIcon = document.createElement('div');

    if (!isRecording) {
        startButton.textContent = 'Stop Recording';
        recordingIcon.id = 'recording-icon';
        recordingIcon.textContent = '🔴 Recording';
        document.body.appendChild(recordingIcon);
        // Implement actual start recording functionality here
        document.getElementById('visualizer').style.display = 'block'; 
        startRecording()
    } else {
        startButton.textContent = 'Start';
        const icon = document.getElementById('recording-icon');
        if (icon) {
            icon.remove();
        }
        // Implement stop recording functionality here
        stopRecording()
        document.getElementById('visualizer').style.display = 'none'; 
    }

    isRecording = !isRecording;
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            source.connect(analyser);
            analyser.fftSize = 2048;
            bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);

            canvas = document.getElementById("visualizer");
            canvasCtx = canvas.getContext("2d");
            drawVisualizer();

            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    recordedChunks.push(event.data);
                }
            };
            mediaRecorder.start();
        })
        .catch(error => {
            console.error("Error accessing microphone:", error);
        });
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder.onstop = async () => {
        const blob = new Blob(recordedChunks, { type: 'audio/webm' });
        const base64Data = await blobToBase64(blob);

        // Save the webm file in localStorage
        localStorage.setItem('recordedAudio', base64Data);
        console.log("Recording saved as webm in localStorage.");

        recordedChunks = []; // Clear the recorded chunks
        audioContext.close();
    };
}

function drawVisualizer() {
    requestAnimationFrame(drawVisualizer);

    analyser.getByteTimeDomainData(dataArray);
    canvasCtx.fillStyle = 'rgb(255, 255, 255)';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
    canvasCtx.beginPath();

    const sliceWidth = canvas.width * 1.0 / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * canvas.height / 2;

        if (i === 0) {
            canvasCtx.moveTo(x, y);
        } else {
            canvasCtx.lineTo(x, y);
        }

        x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
}

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}





async function transcribe() {
    // Assume the WebM file is stored as base64 in localStorage under the key 'audioFile'
    const base64Audio = localStorage.getItem('recordedAudio');
    if (!base64Audio) {
        alert('No audio file found in localStorage!');
        return;
    }

    // Send the base64 audio data to the server for transcription
    try {
        const response = await fetch('http://127.0.0.1:8000/transcribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ audio: base64Audio })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('transcriptionResult').innerText = `Transcription: ${data.transcription}`;
        } else {
            alert('Error transcribing audio');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function submit() {
    //alert('Submit transcript...');
    // Implement transcribe functionality
    const loadingMessage = document.createElement('div');
    document.getElementById('response-link').style.display = 'none'; // Show the response link       
    loadingMessage.id = 'loading-message';
    loadingMessage.textContent = '💀 Connecting with LLM... Please wait.';
    document.body.appendChild(loadingMessage);

    var transcript = document.getElementById('transcript').value;
    transcript =  'Transcript: ' + transcript + '  +   {missing_sections} Return_data_constraints: {constraints}'
    console.log('transcript ' + transcript )
    if (transcript) {
        // Sending the transcript to the web service
        fetch('http://127.0.0.1:8000/acd', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: transcript,     "usecase":"acd",       "page":"ros" })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', JSON.stringify(data));            
            document.getElementById('response-link').style.display = 'block'; // Show the response link            
            sessionStorage.setItem('llmResponse', JSON.stringify(data));
        })
        .catch((error) => {
            console.error('Error:', error);
            
        })
        .finally(() => {            
            if (loadingMessage) {
                loadingMessage.remove();
            }
        });
    } else {
        alert('No transcript available to send.');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
}
function openSettings() {
    alert('Open settings...');
    // Implement open settings functionality
}




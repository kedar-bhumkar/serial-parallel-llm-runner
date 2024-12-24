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
let serverUrl="http://localhost:8000"



function showMessage(type,msg){

    
    document.getElementById('message').classList.add("error");
    if(type=="error"){
        document.getElementById('message').style.color = 'red'; 
    }else{
        document.getElementById('message').style.color = 'green'; 
    }
  
    document.getElementById('message').innerText = type.charAt(0).toUpperCase() + type.slice(1) + ":" + msg 
    document.getElementById('message').style.display = 'block'; 
}

function hideMessage(){
    document.getElementById('message').style.display = 'none'; 
}




function submit() {
    hideMessage();
    managePage("disable");
    const loadingMessage = document.createElement('div');
    document.getElementById('response-link').style.display = 'none';
    loadingMessage.id = 'loading-message';
    loadingMessage.textContent = '💀 Connecting with LLM... Please wait.';
    document.body.appendChild(loadingMessage);

    // Get selected page value
    const selectedPage = document.querySelector('input[name="page"]:checked').value;
    
    var transcript = document.getElementById('transcript').value;
    var idealResponse = document.getElementById('idealResponse').value;
    transcript = 'Transcript: ' + transcript + '  +   {missing_sections} Return_data_constraints: {constraints}';
    console.log('transcript ' + transcript);
    
    if (transcript) {
        fetch(serverUrl+'/acd', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                prompt: transcript,     
                usecase: "acd",       
                page: selectedPage,  // Use the selected page value
                ideal_response: idealResponse
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', JSON.stringify(data));            
            document.getElementById('response-link').style.display = 'block'; // Show the response link            
            sessionStorage.setItem('llmResponse', JSON.stringify(data));
            showMessage("Info", "Response received from LLM. Pls click View response below.")
        })
        .catch((error) => {
            console.error('Error:', error);
            showMessage("error",error)
            
        })
        .finally(() => {            
            if (loadingMessage) {
                loadingMessage.remove();                
            }
            managePage("enable")
        });
    } else {
        alert();
        showMessage("error","No transcript available to send.")
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
}



function managePage(action){
    console.log('Manage page .. action '+ action)

    const allBtn = document.querySelectorAll('button')
       allBtn.forEach((button) => {       
        console.log(button.id)
        if(action == "disable" && button.id != "toggle"){
            console.log('disable...')
            button.disabled = true;
        }
        else if(button.id != "toggle"){
            console.log('enable...')
            button.disabled = false;
        }


    });
}

document.addEventListener('DOMContentLoaded', function() {
    const useIdealResponseCheckbox = document.getElementById('useIdealResponse');
    const idealResponseBox = document.querySelector('.ideal-response-box');

    useIdealResponseCheckbox.addEventListener('change', function() {
        idealResponseBox.style.display = this.checked ? 'block' : 'none';
    });
});

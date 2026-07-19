// // ================================
// // DOM Elements
// // ================================
// console.log("JavaScript Loaded!");
// const form = document.querySelector("form");

// const input = document.getElementById("youtube-url");

// const transcript = document.getElementById("transcript");

// const errorMessage = document.getElementById("error-message");

// const copyBtn = document.getElementById("copy-btn");

// const clearBtn = document.getElementById("clear-btn");


// // ================================
// // Extract YouTube Video ID
// // ================================

// function extractVideoID(url) {

//     try {

//         const parsedUrl = new URL(url);

//         const host = parsedUrl.hostname;

//         // youtube.com/watch?v=
//         if (
//             host.includes("youtube.com") &&
//             parsedUrl.pathname === "/watch"
//         ) {
//             return parsedUrl.searchParams.get("v");
//         }

//         // youtu.be/
//         if (host === "youtu.be") {
//             return parsedUrl.pathname.slice(1);
//         }

//         // youtube.com/shorts/
//         if (
//             host.includes("youtube.com") &&
//             parsedUrl.pathname.startsWith("/shorts/")
//         ) {
//             return parsedUrl.pathname.split("/")[2];
//         }

//         return null;

//     } catch {

//         return null;

//     }

// }

// // ================================
// // Test Flask API
// // ================================

// async function testAPI(url) {

//     try {

//         const response = await fetch("/api/transcript", {

//             method: "POST",

//             headers: {
//                 "Content-Type": "application/json"
//             },

//             body: JSON.stringify({
//                 url: url
//             })

//         });

//         const data = await response.json();

//         transcript.value = JSON.stringify(data, null, 4);

//     }

//     catch (error) {

//         errorMessage.textContent = "❌ Unable to connect to Flask backend.";

//         console.error(error);

//     }

// }
// // // ================================
// // // Form Submit
// // // ================================

// // form.addEventListener("submit", function (e) {

// //     e.preventDefault();

// //     errorMessage.textContent = "";

// //     transcript.value = "";

// //     const url = input.value.trim();

// //     // Empty Input

// //     if (url === "") {

// //         errorMessage.textContent = "⚠ Please enter a YouTube URL.";

// //         return;

// //     }

// //     // Extract ID

// //     const videoID = extractVideoID(url);

// //     if (!videoID) {

// //         errorMessage.textContent = "❌ Invalid YouTube URL.";

// //         return;

// //     }

// //     // Temporary Output

// //     transcript.value =
// // `Video ID Successfully Extracted!

// // ${videoID}

// // ✔ URL is valid.

// // In the next phase,
// // Python will fetch subtitles using this Video ID.`;

// // });
// // ================================
// // Form Submit
// // ================================

// form.addEventListener("submit", async function (e) {

//     e.preventDefault();

//     errorMessage.textContent = "";

//     transcript.value = "";

//     const url = input.value.trim();

//     // Empty Input
//     if (url === "") {

//         errorMessage.textContent = "⚠ Please enter a YouTube URL.";

//         return;

//     }

//     // Validate URL
//     const videoID = extractVideoID(url);

//     if (!videoID) {

//         errorMessage.textContent = "❌ Invalid YouTube URL.";

//         return;

//     }

//     // Show Loading
//     transcript.value = "Connecting to Flask...";

//     // Send request to Flask
//     await testAPI(url);

// });

// // ================================
// // Copy Transcript
// // ================================

// copyBtn.addEventListener("click", async () => {

//     if (transcript.value.trim() === "") {

//         alert("Nothing to copy.");

//         return;

//     }

//     try {

//         await navigator.clipboard.writeText(transcript.value);

//         alert("Transcript copied successfully!");

//     }

//     catch {

//         alert("Copy failed.");

//     }

// });


// // ================================
// // Clear Everything
// // ================================

// clearBtn.addEventListener("click", () => {

//     input.value = "";

//     transcript.value = "";

//     errorMessage.textContent = "";

//     input.focus();

// });


// =========================================
// DOM Elements
// =========================================

const form = document.querySelector("form");

const input = document.getElementById("youtube-url");

const transcript = document.getElementById("transcript");

const errorMessage = document.getElementById("error-message");

const loading = document.getElementById("loading");

const language = document.getElementById("language");

const segments = document.getElementById("segments");

const words = document.getElementById("words");

const characters = document.getElementById("characters");

const timestampBtn = document.getElementById("timestamp-btn");

const rawBtn = document.getElementById("raw-btn");

const searchInput = document.getElementById("search-input");

const clearBtn = document.getElementById("clear-btn");


// =========================================
// Global State
// =========================================

let transcriptData = null;

let currentMode = "timestamp";


// =========================================
// Extract Video ID
// =========================================

function extractVideoID(url){

    try{

        const parsed = new URL(url);

        const host = parsed.hostname;

        if(host.includes("youtube.com") &&
           parsed.pathname === "/watch"){

            return parsed.searchParams.get("v");

        }

        if(host === "youtu.be"){

            return parsed.pathname.substring(1);

        }

        if(parsed.pathname.startsWith("/shorts/")){

            return parsed.pathname.split("/")[2];

        }

        return null;

    }

    catch{

        return null;

    }

}


// =========================================
// Loading
// =========================================

function showLoading(){

    loading.classList.remove("hidden");

    transcript.innerHTML = "";

}

function hideLoading(){

    loading.classList.add("hidden");

}


// =========================================
// Format Time
// =========================================

function formatTime(seconds){

    seconds = Math.floor(seconds);

    const h = Math.floor(seconds / 3600);

    const m = Math.floor((seconds % 3600) / 60);

    const s = seconds % 60;

    if(h > 0){

        return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;

    }

    return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;

}


// =========================================
// Statistics
// =========================================

function updateStats(data){

    language.textContent = data.language;

    segments.textContent = data.segment_count;

    words.textContent = data.word_count;

    characters.textContent = data.character_count;

}


// =========================================
// Render Timestamp View
// =========================================

function renderTimestamp(){

    transcript.innerHTML = "";

    transcriptData.segments.forEach(item=>{

        const row = document.createElement("div");

        row.className = "segment";

        row.innerHTML = `

            <span class="timestamp">

                ${formatTime(item.start)}

            </span>

            <span class="segment-text">

                ${item.text}

            </span>

        `;

        transcript.appendChild(row);

    });

}


// =========================================
// Render Raw View
// =========================================

function renderRaw(){

    transcript.innerHTML = `

        <div class="segment">

            ${transcriptData.raw_text}

        </div>

    `;

}


// =========================================
// Switch View
// =========================================

function renderTranscript(){

    if(!transcriptData) return;

    if(currentMode === "timestamp"){

        renderTimestamp();

    }

    else{

        renderRaw();

    }

}


// =========================================
// Fetch Transcript
// =========================================

async function fetchTranscript(url){

    try{

        showLoading();

        const response = await fetch("/api/transcript",{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                url:url

            })

        });

        const data = await response.json();

        hideLoading();

        if(!data.success){

            errorMessage.textContent = data.error;

            return;

        }

        transcriptData = data;

        updateStats(data);

        renderTranscript();
        initializeSearch();

    }

    catch(error){

        hideLoading();

        errorMessage.textContent = "Unable to connect to Flask backend.";

        console.error(error);

    }

}


// =========================================
// Form Submit
// =========================================

form.addEventListener("submit",async function(e){

    e.preventDefault();

    errorMessage.textContent = "";

    const url = input.value.trim();

    if(url===""){

        errorMessage.textContent = "Please enter a YouTube URL.";

        return;

    }

    const id = extractVideoID(url);

    if(!id){

        errorMessage.textContent = "Invalid YouTube URL.";

        return;

    }

    await fetchTranscript(url);

});


// =========================================
// Toggle Buttons
// =========================================

timestampBtn.addEventListener("click",()=>{

    currentMode = "timestamp";

    timestampBtn.classList.add("active");

    rawBtn.classList.remove("active");

    renderTranscript();

});

rawBtn.addEventListener("click",()=>{

    currentMode = "raw";

    rawBtn.classList.add("active");

    timestampBtn.classList.remove("active");

    renderTranscript();

});


// =========================================
// Clear
// =========================================

clearBtn.addEventListener("click",()=>{

    input.value="";

    transcript.innerHTML = `

        <p class="placeholder">

            Your transcript will appear here after generating subtitles.

        </p>

    `;

    transcriptData = null;

    errorMessage.textContent="";

    language.textContent="-";

    segments.textContent="0";

    words.textContent="0";

    characters.textContent="0";

    searchInput.value="";

});


// =========================================
// Escape HTML
// =========================================

function escapeHTML(text){

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


// =========================================
// Highlight Search
// =========================================

function highlight(text, keyword){

    if(!keyword) return escapeHTML(text);

    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");

    const regex = new RegExp(`(${escaped})`, "gi");

    return escapeHTML(text).replace(

        regex,

        "<mark>$1</mark>"

    );

}


// =========================================
// Search Renderer
// =========================================

function renderSearch(keyword){

    if(!transcriptData) return;

    transcript.innerHTML = "";

    if(currentMode === "raw"){

        transcript.innerHTML = `

            <div class="segment">

                ${highlight(transcriptData.raw_text, keyword)}

            </div>

        `;

        return;

    }

    transcriptData.segments.forEach(item=>{

        const row = document.createElement("div");

        row.className = "segment";

        row.innerHTML = `

            <span class="timestamp">

                ${formatTime(item.start)}

            </span>

            <span class="segment-text">

                ${highlight(item.text, keyword)}

            </span>

        `;

        transcript.appendChild(row);

    });

}


// =========================================
// Search
// =========================================

function initializeSearch(){

    searchInput.value = "";

}


searchInput.addEventListener("input",()=>{

    const keyword = searchInput.value.trim();

    if(keyword === ""){

        renderTranscript();

        return;

    }

    renderSearch(keyword);

});


// =========================================
// Copy Buttons
// =========================================

const copyRawBtn = document.getElementById("copy-raw-btn");

const copyTimeBtn = document.getElementById("copy-time-btn");


copyRawBtn.addEventListener("click", async ()=>{

    if(!transcriptData){

        alert("No transcript available.");

        return;

    }

    try{

        await navigator.clipboard.writeText(

            transcriptData.raw_text

        );

        alert("Raw transcript copied.");

    }

    catch{

        alert("Copy failed.");

    }

});


copyTimeBtn.addEventListener("click", async ()=>{

    if(!transcriptData){

        alert("No transcript available.");

        return;

    }

    let output = "";

    transcriptData.segments.forEach(item=>{

        output +=

`${formatTime(item.start)}
${item.text}

`;

    });

    try{

        await navigator.clipboard.writeText(output);

        alert("Timestamped transcript copied.");

    }

    catch{

        alert("Copy failed.");

    }

});


// =========================================
// Download TXT
// =========================================

const downloadBtn = document.getElementById("download-btn");


downloadBtn.addEventListener("click",()=>{

    if(!transcriptData){

        alert("Nothing to download.");

        return;

    }

    let content = "";

    if(currentMode === "raw"){

        content = transcriptData.raw_text;

    }

    else{

        transcriptData.segments.forEach(item=>{

            content +=

`${formatTime(item.start)}
${item.text}

`;

        });

    }

    const blob = new Blob(

        [content],

        {

            type:"text/plain"

        }

    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "youtube_transcript.txt";

    a.click();

    URL.revokeObjectURL(url);

});


// =========================================
// Keyboard Shortcut
// Ctrl + Enter
// =========================================

input.addEventListener("keydown",(e)=>{

    if(e.ctrlKey && e.key==="Enter"){

        form.requestSubmit();

    }

});


// =========================================
// Initial Placeholder
// =========================================

transcript.innerHTML = `

<p class="placeholder">

Paste a YouTube URL and click
<strong>Generate Transcript</strong>.

</p>

`;
/* ===== FULL LMS IN ONE JS FILE ===== */

(function() {
    // Attach main container
    const container = document.createElement('div');
    container.style.width = "90%";
    container.style.maxWidth = "900px";
    container.style.margin = "20px auto";
    container.style.fontFamily = "Segoe UI, Arial, sans-serif";
    document.body.appendChild(container);

    let currentUserRole = '';

    // ---------- LOGIN FORM ----------
    const loginSection = document.createElement('div');
    loginSection.id = 'loginSection';
    loginSection.innerHTML = `
        <h2>Login</h2>
        <input type="email" id="loginEmail" placeholder="Email" required style="width:100%;padding:10px;margin:5px 0;">
        <input type="password" id="loginPassword" placeholder="Password" required style="width:100%;padding:10px;margin:5px 0;">
        <button id="loginBtn" style="padding:10px 20px;margin-top:10px;">Login</button>
    `;
    container.appendChild(loginSection);

    // ---------- OTP VERIFICATION ----------
    const otpSection = document.createElement('div');
    otpSection.id = 'otpSection';
    otpSection.style.display = 'none';
    otpSection.innerHTML = `
        <h2>OTP Verification</h2>
        <input type="text" id="otpInput" placeholder="Enter 6-digit OTP" style="width:100%;padding:10px;margin:5px 0;">
        <button id="verifyOtpBtn" style="padding:10px 20px;margin-top:10px;">Verify OTP</button>
    `;
    container.appendChild(otpSection);

    // ---------- STUDENT DASHBOARD ----------
    const studentDashboard = document.createElement('div');
    studentDashboard.id = 'studentDashboard';
    studentDashboard.style.display = 'none';
    studentDashboard.innerHTML = `
        <h2>Student Dashboard</h2>
        <div id="pdfs"></div>
        <div id="videos"></div>
        <div id="quizzes"></div>
    `;
    container.appendChild(studentDashboard);

    // ---------- ADMIN DASHBOARD ----------
    const adminDashboard = document.createElement('div');
    adminDashboard.id = 'adminDashboard';
    adminDashboard.style.display = 'none';
    adminDashboard.innerHTML = `
        <h2>Admin Dashboard</h2>
        <h3>Upload PDF</h3>
        <input type="text" id="pdfTitle" placeholder="PDF Title" style="width:100%;padding:8px;margin:5px 0;">
        <input type="file" id="pdfFile" style="margin:5px 0;">
        <button id="uploadPDFBtn" style="padding:8px 15px;">Upload PDF</button>
        <h3>Add Video</h3>
        <input type="text" id="videoTitle" placeholder="Video Title" style="width:100%;padding:8px;margin:5px 0;">
        <input type="text" id="videoURL" placeholder="Video URL" style="width:100%;padding:8px;margin:5px 0;">
        <button id="addVideoBtn" style="padding:8px 15px;">Add Video</button>
        <h3>Add Quiz</h3>
        <input type="text" id="quizQuestion" placeholder="Question" style="width:100%;padding:8px;margin:5px 0;">
        <input type="text" id="quizOptions" placeholder="Options (comma separated)" style="width:100%;padding:8px;margin:5px 0;">
        <input type="text" id="quizAnswer" placeholder="Answer" style="width:100%;padding:8px;margin:5px 0;">
        <button id="addQuizBtn" style="padding:8px 15px;">Add Quiz</button>
    `;
    container.appendChild(adminDashboard);

    // ---------- FUNCTIONALITY ----------
    async function loginUser() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        // Mock login for demo, replace with real backend fetch
        if(email==='admin@example.com' && password==='admin123'){
            currentUserRole='admin';
        } else if(email==='student@example.com' && password==='student123'){
            currentUserRole='student';
        } else {
            alert('Invalid credentials');
            return;
        }

        loginSection.style.display='none';
        otpSection.style.display='block';
    }

    async function verifyOtp() {
        const otp = document.getElementById('otpInput').value;
        if(otp.length !== 6){
            alert('Enter valid 6-digit OTP');
            return;
        }

        otpSection.style.display='none';
        if(currentUserRole==='student'){
            studentDashboard.style.display='block';
            loadStudentContent();
        } else {
            adminDashboard.style.display='block';
        }
    }

    function loadStudentContent() {
        const pdfsDiv = document.getElementById('pdfs');
        const videosDiv = document.getElementById('videos');
        const quizzesDiv = document.getElementById('quizzes');

        pdfsDiv.innerHTML='<h3>PDF Notes</h3>';
        videosDiv.innerHTML='<h3>Video Tutorials</h3>';
        quizzesDiv.innerHTML='<h3>Quizzes</h3>';

        // Mock content, replace with backend fetch
        const pdfs=[{title:'Health Notes', url:'#'},{title:'IoT Notes', url:'#'}];
        const videos=[{title:'JS Tutorial', url:'https://www.youtube.com/embed/MkC46GqHo40'}];
        const quizzes=[{question:'What is JS?', options:['Lang','Fruit','Car'], answer:'Lang'}];

        pdfs.forEach(pdf=>{
            const a=document.createElement('a');
            a.href=pdf.url; a.target='_blank'; a.textContent=pdf.title;
            pdfsDiv.appendChild(a);
            pdfsDiv.appendChild(document.createElement('br'));
        });

        videos.forEach(video=>{
            const iframe=document.createElement('iframe');
            iframe.src=video.url;
            iframe.width=300; iframe.height=180;
            iframe.style.margin='10px 0';
            videosDiv.appendChild(iframe);
        });

        quizzes.forEach((q,i)=>{
            const div=document.createElement('div');
            div.innerHTML=`<strong>Q${i+1}:</strong> ${q.question}<br>`;
            q.options.forEach(opt=>{
                div.innerHTML+=`<input type="radio" name="q${i}" value="${opt}"> ${opt}<br>`;
            });
            quizzesDiv.appendChild(div);
            quizzesDiv.appendChild(document.createElement('hr'));
        });
    }

    function uploadPDF(){
        alert('PDF Uploaded (Demo)'); // Replace with backend upload
    }
    function addVideo(){
        alert('Video Added (Demo)');
    }
    function addQuiz(){
        alert('Quiz Added (Demo)');
    }

    // ---------- EVENT LISTENERS ----------
    document.getElementById('loginBtn').addEventListener('click', loginUser);
    document.getElementById('verifyOtpBtn').addEventListener('click', verifyOtp);
    document.getElementById('uploadPDFBtn').addEventListener('click', uploadPDF);
    document.getElementById('addVideoBtn').addEventListener('click', addVideo);
    document.getElementById('addQuizBtn').addEventListener('click', addQuiz);

})();

// Saylo AI Interview Platform - Frontend JavaScript

const API_BASE = 'http://localhost:8000/api';
let currentSessionId = null;
let currentQuestionId = null;
let currentQuestionNumber = 1;

// Utility Functions
function showStatus(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status ${type}`;
    element.style.display = 'block';
}

function hideStatus(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
}

// Upload Resume
async function uploadResume() {
    const fileInput = document.getElementById('resume-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('resume-status', 'Please select a file', 'error');
        return;
    }
    
    showStatus('resume-status', 'Uploading and processing resume...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', 'default');
    
    try {
        const response = await fetch(`${API_BASE}/upload/resume`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('resume-status', `✓ Resume uploaded successfully! Found skills: ${data.parsed_data.skills.join(', ')}`, 'success');
        } else {
            showStatus('resume-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('resume-status', `Error: ${error.message}`, 'error');
    }
}

// Upload Reference Document
async function uploadReference() {
    const fileInput = document.getElementById('reference-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('reference-status', 'Please select a file', 'error');
        return;
    }
    
    showStatus('reference-status', 'Uploading and processing reference document...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', 'default');
    
    try {
        const response = await fetch(`${API_BASE}/upload/reference`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('reference-status', `✓ Reference document uploaded! Created ${data.chunk_count} chunks for context retrieval.`, 'success');
        } else {
            showStatus('reference-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('reference-status', `Error: ${error.message}`, 'error');
    }
}

// Create Session
async function createSession() {
    const subjectName = document.getElementById('subject-name').value;
    
    if (!subjectName) {
        showStatus('session-status', 'Please enter a subject name', 'error');
        return;
    }
    
    showStatus('session-status', 'Creating interview session...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/sessions/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject_name: subjectName,
                resume_path: 'data/uploads/resume_default.pdf',
                reference_doc_path: 'data/uploads/reference_default.pdf'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentSessionId = data.session_id;
            showStatus('session-status', `✓ Session created! ID: ${currentSessionId}`, 'success');
            
            // Show interview section
            document.getElementById('interview-section').style.display = 'block';
        } else {
            showStatus('session-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('session-status', `Error: ${error.message}`, 'error');
    }
}

// Start Interview
async function startInterview() {
    if (!currentSessionId) {
        showStatus('interview-status', 'Please create a session first', 'error');
        return;
    }
    
    showStatus('interview-status', 'Starting interview...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/sessions/${currentSessionId}/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('interview-status', '✓ Interview started!', 'success');
            
            // Update UI
            document.getElementById('start-btn').style.display = 'none';
            document.getElementById('end-btn').style.display = 'inline-block';
            
            // Generate first question
            await generateQuestion();
        } else {
            showStatus('interview-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('interview-status', `Error: ${error.message}`, 'error');
    }
}

// Generate Question
async function generateQuestion() {
    showStatus('interview-status', `Generating question ${currentQuestionNumber}...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/interview/generate-question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question_number: currentQuestionNumber
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentQuestionId = data.question_id;
            
            // Display question
            document.getElementById('question-container').style.display = 'block';
            document.getElementById('question-number').textContent = currentQuestionNumber;
            document.getElementById('question-text').textContent = data.question_text;
            document.getElementById('answer-text').value = '';
            document.getElementById('evaluation-result').innerHTML = '';
            
            showStatus('interview-status', '✓ Question generated!', 'success');
        } else {
            showStatus('interview-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('interview-status', `Error: ${error.message}`, 'error');
    }
}

// Submit Answer
async function submitAnswer() {
    const answerText = document.getElementById('answer-text').value;
    
    if (!answerText.trim()) {
        showStatus('interview-status', 'Please provide an answer', 'error');
        return;
    }
    
    showStatus('interview-status', 'Evaluating your answer...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/interview/submit-answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question_id: currentQuestionId,
                answer_text: answerText
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const evaluation = data.evaluation;
            
            // Display evaluation
            const evalHtml = `
                <h4>📊 Evaluation Results</h4>
                <div class="analytics-metric">
                    <strong>Overall Score:</strong>
                    <span>${evaluation.overall_score}/10</span>
                </div>
                <div class="analytics-metric">
                    <strong>Correctness:</strong>
                    <span>${evaluation.correctness_score}/10</span>
                </div>
                <div class="analytics-metric">
                    <strong>Completeness:</strong>
                    <span>${evaluation.completeness_score}/10</span>
                </div>
                <div class="analytics-metric">
                    <strong>Clarity:</strong>
                    <span>${evaluation.clarity_score}/10</span>
                </div>
                <div style="margin-top: 15px;">
                    <strong>Feedback:</strong>
                    <p style="margin-top: 10px;">${evaluation.feedback}</p>
                </div>
                ${evaluation.strengths && evaluation.strengths.length > 0 ? `
                    <div style="margin-top: 15px;">
                        <strong>Strengths:</strong>
                        <ul style="margin-top: 5px;">
                            ${evaluation.strengths.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${evaluation.improvements && evaluation.improvements.length > 0 ? `
                    <div style="margin-top: 15px;">
                        <strong>Areas for Improvement:</strong>
                        <ul style="margin-top: 5px;">
                            ${evaluation.improvements.map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
            
            document.getElementById('evaluation-result').innerHTML = evalHtml;
            showStatus('interview-status', '✓ Answer evaluated!', 'success');
            
            // Ask if user wants next question
            if (currentQuestionNumber < 8) {
                setTimeout(() => {
                    if (confirm('Ready for the next question?')) {
                        currentQuestionNumber++;
                        generateQuestion();
                    }
                }, 2000);
            } else {
                setTimeout(() => {
                    alert('Interview complete! Ending session...');
                    endInterview();
                }, 2000);
            }
        } else {
            showStatus('interview-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('interview-status', `Error: ${error.message}`, 'error');
    }
}

// End Interview
async function endInterview() {
    if (!currentSessionId) {
        return;
    }
    
    showStatus('interview-status', 'Ending interview...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/sessions/${currentSessionId}/end`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('interview-status', `✓ Interview ended! Duration: ${data.duration_seconds}s`, 'success');
            
            // Hide interview section, show analytics
            document.getElementById('interview-section').style.display = 'none';
            document.getElementById('analytics-section').style.display = 'block';
            
            // Load analytics
            loadAnalytics();
        } else {
            showStatus('interview-status', `Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus('interview-status', `Error: ${error.message}`, 'error');
    }
}

// Load Analytics
async function loadAnalytics() {
    try {
        // Get transcript
        const transcriptResponse = await fetch(`${API_BASE}/interview/${currentSessionId}/transcript`);
        const transcript = await transcriptResponse.json();
        
        // Get questions
        const questionsResponse = await fetch(`${API_BASE}/interview/${currentSessionId}/questions`);
        const questions = await questionsResponse.json();
        
        // Display analytics
        let analyticsHtml = `
            <h3>📝 Session Summary</h3>
            <div class="analytics-metric">
                <strong>Questions Answered:</strong>
                <span>${questions.length}</span>
            </div>
            <div class="analytics-metric">
                <strong>Transcript Entries:</strong>
                <span>${transcript.length}</span>
            </div>
            
            <h3 style="margin-top: 30px;">❓ Questions & Answers</h3>
        `;
        
        questions.forEach((q, i) => {
            analyticsHtml += `
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong>Q${i + 1}:</strong> ${q.question_text}
                    <br><br>
                    <strong>Your Answer:</strong> ${q.user_answer || 'Not answered'}
                    <br><br>
                    <strong>Response Time:</strong> ${q.response_time_seconds ? q.response_time_seconds.toFixed(1) + 's' : 'N/A'}
                </div>
            `;
        });
        
        document.getElementById('analytics-content').innerHTML = analyticsHtml;
        
    } catch (error) {
        document.getElementById('analytics-content').innerHTML = `<p class="status error">Error loading analytics: ${error.message}</p>`;
    }
}

// Check API health on load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        
        if (data.services.ollama !== 'healthy') {
            alert('Warning: Ollama service is not running. Please start Ollama before using the platform.');
        }
    } catch (error) {
        alert('Warning: Cannot connect to backend API. Please ensure the backend is running on http://localhost:8000');
    }
});

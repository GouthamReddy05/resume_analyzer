class ResumeAnalyzer {
    constructor() {
        this.uploadedFile = null;
        this.formData = {};
        this.sessionId = null;
        this.activeFeature = 'analysis';
        this.analysisResults = {};
        this.processingStatus = {};
        this.apiBaseUrl = 'http://localhost:5000';

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
    }

    setupEventListeners() {
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('click', () => this.selectFeature(card.dataset.feature));
        });

        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        document.getElementById('analyzeBtn').addEventListener('click', () => this.startAnalysis());

        document.querySelectorAll('.form-control, input[type="checkbox"]').forEach(input => {
            input.addEventListener('change', () => this.updateFormData());
        });

        document.getElementById('aiChat').addEventListener('click', () => this.openAIChat());
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('resumeFile');

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    handleFileUpload(file) {
        if (!this.validateFile(file)) return;

        this.uploadedFile = file;
        this.updateUploadUI(file);
    }

    validateFile(file) {
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!allowedTypes.includes(file.type)) {
            this.showMessage('Please upload a PDF, DOC, or DOCX file.', 'error');
            return false;
        }

        if (file.size > maxSize) {
            this.showMessage('File size should be less than 5MB.', 'error');
            return false;
        }

        return true;
    }

    updateUploadUI(file) {
        const uploadArea = document.getElementById('uploadArea');
        const uploadText = uploadArea.querySelector('.upload-text');

        uploadText.textContent = `✅ ${file.name} uploaded successfully`;
        uploadArea.classList.add('uploaded');
        uploadArea.style.background = 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)';
        uploadArea.style.borderColor = '#28a745';
    }

    updateFormData() {
        this.formData = {
            jobTitle: document.getElementById('jobTitle').value.trim(),
            experience: document.getElementById('experience').value,
            jobDescription: document.getElementById('jobDescription').value.trim(),
            location: document.getElementById('location').value,
            preferences: Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value),
            timestamp: new Date().toISOString()
        };
    }

    validateForm() {
        if (!this.uploadedFile) {
            this.showMessage('Please upload your resume first.', 'error');
            return false;
        }

        if (!this.formData.jobTitle) {
            this.showMessage('Please enter a target job title.', 'error');
            return false;
        }

        if (!this.formData.experience) {
            this.showMessage('Please select your experience level.', 'error');
            return false;
        }

        if (!this.formData.location) {
            this.showMessage('Please enter the location.', 'error');
            return false;
        }

        return true;
    }

    async startAnalysis() {
        this.updateFormData();

        if (!this.validateForm()) return;

        // Reset analysis state
        this.resetAnalysisState();

        // Show loading
        this.showLoading('Initializing analysis...');
        this.setAnalyzeButtonState(true);

        try {
            // Upload resume and create session
            const sessionResult = await this.createAnalysisSession();
            this.sessionId = sessionResult.session_id;

            this.showLoading('Processing resume content...');

            // Show results section
            document.getElementById('results').classList.add('show');

            // Start parallel analysis for all features
            await this.startParallelAnalysis();

        } catch (error) {
            console.error('Analysis failed:', error);
            this.handleAnalysisError(error);
        } finally {
            this.hideLoading();
            this.setAnalyzeButtonState(false);
        }
    }

    async createAnalysisSession() {
        const formData = new FormData();
        formData.append('resume_file', this.uploadedFile);
        formData.append('form_data', JSON.stringify(this.formData));

        const response = await fetch(`${this.apiBaseUrl}/upload_resume`, {
            method: 'POST',
            body: formData,
            credentials: 'include'

        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }

        return await response.json();
    }

    async startParallelAnalysis() {
        try {

            // const sessionResponse = await this.createAnalysisSession();
            // this.sessionId = sessionResponse.session_id; 

            const features = [
                'analysis',
                'skills',
                'interview',
                'project_ideas',
                'keyword_optimizer',
                'live_job_feed'
            ];


            const analysisPromises = features.map(feature =>
                this.analyzeFeature(feature)
            );

            await Promise.allSettled(analysisPromises);

            this.showMessage(
                'Analysis completed! Click on different tabs to explore results.',
                'success'
            );
        } catch (error) {
            console.error('Error in startParallelAnalysis:', error);
            this.showMessage('Failed to start analysis. Please try again.', 'error');
        }
    }


    async analyzeFeature(featureType) {
        try {
            this.setFeatureStatus(featureType, 'processing');

            const response = await fetch(`${this.apiBaseUrl}/analyze_feature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    feature_type: featureType,
                    form_data: this.formData,
                }),

            });

            if (!response.ok) {
                throw new Error(`Feature analysis failed: ${response.status}`);
            }

            const results = await response.json();
            this.analysisResults[featureType] = results;

            console.log(`Completed ${featureType}:`, results);

            this.updateFeatureUI(featureType, results);
            this.setFeatureStatus(featureType, 'completed');

        } catch (error) {
            console.error(`Error analyzing ${featureType}:`, error);
            this.setFeatureStatus(featureType, 'error');

            // Show demo data as fallback
            console.error(`Error analyzing ${featureType}:`, error);
            const demoResults = this.getDemoResults(featureType);
            this.updateFeatureUI(featureType, demoResults);
            this.setFeatureStatus(featureType, 'completed');
        }
    }


    updateFeatureUI(featureType, results) {
        switch (featureType) {
            case 'analysis':
                this.updateATSAnalysis(results);
                break;
            case 'skills':
                this.updateSkillsAnalysis(results);
                break;
            case 'interview':
                this.updateInterviewAnalysis(results);
                break;
            case 'live_job_feed':
                this.updateJobsAnalysis(results);
                break;
            case 'project_ideas':
                this.updateProjectIdeas(results);
                break;
            case 'keyword_optimizer':
                this.updateKeywordOptimizer(results);
                break;
        }
        this.updateTabBadge(featureType, 'completed');
    }

    updateProjectIdeas(results) {
        const projectIdeasContent = document.getElementById('project_ideas');
        if (!projectIdeasContent) return;
        projectIdeasContent.innerHTML = `
            <div class="analysis-card">
                <h3>💡 Project Ideas</h3>
                <ul>
                    ${results.ideas ? results.ideas.map(idea => `<li>${idea}</li>`).join('') : '<li>No project ideas found.</li>'}
                </ul>
            </div>
        `;
    }

    updateKeywordOptimizer(results) {
        const keywordOptContent = document.getElementById('keyword_optimizer');
        if (!keywordOptContent) return;
        keywordOptContent.innerHTML = `
            <div class="analysis-card">
                <h3>🔑 Keyword Optimizer</h3>
                <ul>
                    ${results.keywords ? results.keywords.map(keyword => `<li>${keyword}</li>`).join('') : '<li>No keywords found.</li>'}
                </ul>
            </div>
        `;
    }


    updateATSAnalysis(results) {
        // Only show ATS score in an attractive way
        const analysisContent = document.getElementById('analysis');
        const atsScore = results.ats_score || 87;
        analysisContent.innerHTML = `
        <div class="analysis-card" style="text-align: center; padding: 40px 20px;">
            <h2 style="font-size: 2.2rem; color: #667eea; margin-bottom: 20px;">ATS Score</h2>
            <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
                <div style="width: 140px; height: 140px; border-radius: 50%; background: linear-gradient(135deg, #667eea 60%, #27ae60 100%); display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 24px rgba(102,126,234,0.15);">
                    <span style="font-size: 3.5rem; font-weight: 700; color: #fff;">${atsScore}</span>
                    <span style="font-size: 1.1rem; color: #e0e0e0;">out of 100</span>
                </div>
            </div>
            <p style="font-size: 1.1rem; color: #444; margin-bottom: 0;">This score reflects how well your resume matches the job description for ATS (Applicant Tracking System) screening.</p>
        </div>
    `;
    }

    updateSkillsAnalysis(results) {
        const skillsContent = document.getElementById('skills');
        skillsContent.innerHTML = `
                    <div class="analysis-grid">
                        <div class="analysis-card">
                            <h3>🎯 Current Skills</h3>
                            <div style="margin-bottom: 20px;">
                                ${results.existing_skills ? results.existing_skills.map(skill =>
            `<div class="skill-tag">${skill}</div>`
        ).join('') : ''}
                            </div>
                        </div>
                        <div class="analysis-card">
                            <h3>❌ Missing Skills</h3>
                            <div style="margin-bottom: 20px;">
                                ${results.missing_skills ? results.missing_skills.map(skill =>
            `<div class="skill-tag missing-skill">${skill}</div>`
        ).join('') : ''}
                            </div>
                        </div>
                    </div> 
                    
                    ${results.skill_gaps ? `
                    <div style="margin-top: 30px;">
                        <h3 style="color: #667eea; margin-bottom: 20px;">📚 Learning Path Recommendations</h3>
                        <div class="analysis-grid">
                            ${results.skill_gaps.map(gap => `
                                <div class="analysis-card">
                                    <h4 style="color: #e74c3c;">${gap.category}</h4>
                                    <p><strong>Importance:</strong> <span style="color: ${gap.importance === 'High' ? '#e74c3c' : gap.importance === 'Medium' ? '#f39c12' : '#27ae60'}">${gap.importance}</span></p>
                                    <p><strong>Skills to learn:</strong> ${gap.skills.join(', ')}</p>
                                    <p style="font-size: 0.9em; color: #666; margin-top: 10px;"><strong>Learning Path:</strong> ${gap.learning_path}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                `;
    }

    updateInterviewAnalysis(results) {
        const interviewContent = document.getElementById('interview');
        interviewContent.innerHTML = `
            <div class="analysis-card" style="margin-bottom: 30px;">
                <h3>🎤 Personalized Interview Questions</h3>
                <div id="interview-questions">
                    ${results.questions ? results.questions.slice(0, 20).map((q, index) => `
                        <div class="interview-question">
                            <strong>Q${index + 1}: ${q.question}</strong>
                        </div>
                    `).join('') : '<div>No questions found.</div>'}
                </div>
            </div>
        `;
    }

    updateJobsAnalysis(results) {
        const jobsContent = document.getElementById('live_job_feed');
        jobsContent.innerHTML = `
        <div class="analysis-card" style="margin-bottom: 30px;">
            <h3>💼 Top Job Matches</h3>
            <div>
                ${results.matches ? results.matches.slice(0, 20).map(job => `
                    <div class="job-match-card" style="margin-bottom: 18px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="color: #667eea; margin-bottom: 5px;">${job.title}</h4>
                                <p style="margin: 0;"><strong>${job.company}</strong> • ${job.location}</p>
                            </div>
                            <div class="job-match-score">${job.match_score}% Match</div>
                        </div>
                    </div>
                `).join('') : '<div>No jobs found.</div>'}
            </div>
        </div>
    `;
    }

    setFeatureStatus(featureType, status) {
        const featureCard = document.querySelector(`[data-feature="${featureType}"]`);
        const statusIcon = document.getElementById(`${featureType}-status`);

        if (!featureCard) {
            console.warn(`Feature card not found: ${featureType}`);
            return;
        }

        if (!statusIcon) {
            console.warn(`Status icon not found: ${featureType}-status`);
        }

        featureCard.classList.remove('processing', 'completed', 'error');

        switch (status) {
            case 'processing':
                featureCard.classList.add('processing');
                if (statusIcon) statusIcon.textContent = '⏳';
                break;
            case 'completed':
                featureCard.classList.add('completed');
                if (statusIcon) statusIcon.textContent = '✅';
                break;
            case 'error':
                if (statusIcon) statusIcon.textContent = '❌';
                break;
            default:
                if (statusIcon) statusIcon.textContent = '';
        }

        this.processingStatus[featureType] = status;
    }

    updateTabBadge(tabName, status) {
        const badge = document.getElementById(`${tabName}-badge`);
        if (!badge) return;

        badge.classList.remove('completed');
        if (status === 'completed') {
            badge.classList.add('completed');
        }
    }

    selectFeature(featureType) {
        // Update UI
        document.querySelectorAll('.feature-card').forEach(card =>
            card.classList.remove('active'));
        document.querySelector(`[data-feature="${featureType}"]`).classList.add('active');

        this.activeFeature = featureType;

        // Switch to corresponding tab if results are shown
        if (document.getElementById('results').classList.contains('show')) {
            this.switchTab(featureType === 'analysis' ? 'analysis' : featureType);
        }
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active content
        document.querySelectorAll('.tab-content').forEach(content =>
            content.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
    }

    animateScore(targetScore = 87) {
        const scoreElement = document.getElementById('atsScore');
        let currentScore = 0;
        const increment = targetScore / 50;
        const timer = setInterval(() => {
            currentScore += increment;
            if (currentScore >= targetScore) {
                currentScore = targetScore;
                clearInterval(timer);
            }
            scoreElement.textContent = Math.floor(currentScore);
        }, 30);
    }

    showLoading(message = 'Processing...') {
        document.getElementById('loadingText').textContent = message;
        document.getElementById('loading').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading').classList.remove('show');
    }

    setAnalyzeButtonState(loading) {
        const button = document.getElementById('analyzeBtn');
        const spinner = document.getElementById('analyzeSpinner');

        button.disabled = loading;
        spinner.style.display = loading ? 'inline-block' : 'none';
    }

    showMessage(message, type = 'info') {
        const statusDiv = document.getElementById('analysisStatus');
        statusDiv.innerHTML = `
                    <div class="${type === 'error' ? 'error-message' : 'success-message'}">
                        ${message}
                    </div>
                `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 5000);
    }

    resetAnalysisState() {
        this.analysisResults = {};
        this.processingStatus = {};
    this.sessionId = null; // Reset sessionId

        // Reset feature statuses
    ['analysis', 'skills', 'interview', 'live_job_feed', 'project_ideas', 'keyword_optimizer'].forEach(feature => {
            this.setFeatureStatus(feature, '');
            this.updateTabBadge(feature, '');
        });

        // Hide score card
        document.getElementById('scoreCard').style.display = 'none';

        // Reset tab contents to empty states
        this.resetTabContents();
    }

    resetTabContents() {
        const emptyStates = {
            analysis: {
                icon: '📊',
                title: 'Analysis in Progress',
                description: 'Your resume analysis will appear here once processing is complete.'
            },
            skills: {
                icon: '🎯',
                title: 'Skill Analysis Pending',
                description: 'Skill gap analysis and recommendations will be generated based on your target role.'
            },
            interview: {
                icon: '🎤',
                title: 'Interview Questions Coming Soon',
                description: 'Personalized interview questions will be generated based on your resume and target role.'
            },
            project_ideas: {
                icon: '🛠️',
                title: 'Project Ideas',
                description: 'AI-generated project ideas will appear here after analysis.'
            },
            keyword_optimizer: {
                icon: '🔍',
                title: 'Keyword Optimizer',
                description: 'Optimized keywords for your resume will appear here after analysis.'
            },
            live_job_feed: {
                icon: '💼',
                title: 'Job Matching in Progress',
                description: 'Relevant job opportunities will be matched based on your profile analysis.'
            }
        };

        Object.keys(emptyStates).forEach(tabName => {
            const state = emptyStates[tabName];
            const element = document.getElementById(tabName);
            if (!element) {
                console.warn(`Tab content not found: ${tabName}`);
                return;
            }
            element.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${state.icon}</div>
                <h3>${state.title}</h3>
                <p>${state.description}</p>
            </div>
        `;
        });
    }

    handleAnalysisError(error) {
        this.showMessage(`Backend connection failed: ${error.message}. Please ensure your backend server is running.`, 'error');

        // Don't show results section for now - keep it clean
        // document.getElementById('results').classList.add('show');

        // Reset to empty states
        this.resetAnalysisState();
    }

    openAIChat() {
        const context = this.formData.jobTitle ? `for ${this.formData.jobTitle} role` : '';
        const hasResults = Object.keys(this.analysisResults).length > 0;

        let message = "🤖 AI Career Assistant: \"Hello! I can help you improve your resume";
        if (context) message += ` ${context}`;
        message += ".";

        if (hasResults) {
            message += " I can see your analysis is complete. What specific area would you like to focus on?\"";
        } else {
            message += " Upload your resume and fill in the details to get started with personalized insights!\"";
        }

        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('analyzeBtn');  // ✅ Define it first
    console.log('Analyze Button:', btn);               // ✅ Then use it
    const resumeAnalyzer = new ResumeAnalyzer();
});
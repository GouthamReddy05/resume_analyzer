
from flask import Flask, render_template, request, jsonify, session
import json
from flask_cors import CORS
from files.missing_skills import generate_missing_skills, retrieve_skills, send_text_to_llm, extract_ordered_text_pdf
from files.interview_prep import generate_interview_questions
import os
import uuid
from werkzeug.utils import secure_filename
from flask_session import Session





app = Flask(__name__)
app.secret_key = 'super_secret_key_2025'  # Required for session usage
# CORS(app, supports_credentials=True)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app, supports_credentials=True)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():


    try:
        resume_file = request.files.get('resume_file')
        form_data_raw = request.form.get('form_data')
        if not resume_file:
            app.logger.error("No file uploaded")
            return "No file uploaded", 400

        try:
            resume_text = extract_ordered_text_pdf(resume_file)
        except Exception as e:
            app.logger.error(f"Error extracting text from PDF: {e}")
            return jsonify({"error": f"PDF extraction failed: {str(e)}"}), 500

        session["resume_text"] = resume_text

        form_data = None
        if form_data_raw:
            try:
                form_data = json.loads(form_data_raw)
            except Exception as e:
                app.logger.error(f"Invalid form_data: {form_data_raw} | Error: {e}")
                return jsonify({"error": "Invalid form_data"}), 400

        # ✅ Generate a unique session_id
        session_id = str(uuid.uuid4())
        session[session_id] = {
            "resume_text": resume_text,
            "form_data": form_data
        }

        # ✅ Return session_id so frontend can use it later
        return jsonify({
            "message": "Resume uploaded successfully",
            "session_id": session_id
        })

    except Exception as e:
        app.logger.error(f"Upload Resume Error: {e}")
        return jsonify({"error": str(e)}), 500
    


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')



@app.route('/analyze_feature', methods=['POST'])
def analyze_feature():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        app.logger.info(f"Incoming session_id: {session_id}")
        app.logger.info(f"Current session contents: {dict(session)}")
        session_data = session.get(session_id)
        if not session_data or "resume_text" not in session_data:
            app.logger.error(f"Session data not found for session_id: {session_id}")
            return jsonify({'error': 'No resume uploaded'}), 400

        feature_type = data.get('feature_type')
        form_data = data.get('form_data')
        # Use form_data from session if not provided in request
        if not form_data:
            form_data = session_data.get('form_data', {})

        job_title = form_data.get('jobTitle') if form_data else None
        experience_level = form_data.get('experience') if form_data else None
        job_description = form_data.get('jobDescription') if form_data else None
        location = form_data.get('location') if form_data else None

        resume_text = session_data.get('resume_text')

        if not resume_text:
            return jsonify({'error': 'No resume uploaded'}), 400
        



        # Now analyze based on feature type
        if feature_type == 'analysis':
            return jsonify({
                'ats_score': 87,
                'strengths': ['Python', 'Machine Learning', 'Teamwork'],
                'improvements': [
                    {'area': 'Leadership', 'score': 60, 'description': 'Lead more projects.'},
                    {'area': 'Cloud', 'score': 50, 'description': 'Get certified in AWS.'}
                ],
                'summary': 'Strong technical background with room for leadership growth.'
            })

        elif feature_type == 'skills':
            # ✅ Use actual resume path from session

            structured_text = send_text_to_llm(resume_text)
            skills = retrieve_skills(structured_text)
            missing_skills = generate_missing_skills(job_title, skills)


            return jsonify(missing_skills)

        elif feature_type == 'interview':
            return jsonify({
                'questions': [
                    {
                        'question': 'Tell me about yourself.',
                        'difficulty': 'Easy',
                        'category': 'General',
                        'tips': 'Focus on your strengths.'
                    },
                    {
                        'question': 'How do you handle conflict?',
                        'difficulty': 'Medium',
                        'category': 'Behavioral',
                        'tips': 'Give a real example.'
                    }
                ],
                'preparation_tips': ['Research the company.', 'Practice common questions.']
            })

        elif feature_type == 'live_job_feed':
            return jsonify({
                'matches': [
                    {
                        'title': 'Data Scientist',
                        'company': 'TechCorp',
                        'location': 'Remote',
                        'salary_range': '$100k-$120k',
                        'job_type': 'Full-time',
                        'remote_option': True,
                        'match_score': 92,
                        'description': 'Work on ML models.',
                        'key_requirements': ['Python', 'ML'],
                        'missing_requirements': ['AWS']
                    }
                ],
                'market_insights': {
                    'average_salary': '$110k',
                    'job_growth': '12%',
                    'top_skills_demand': ['Python', 'ML'],
                    'trending_technologies': ['AI', 'Cloud']
                }
            })

        elif feature_type == 'project_ideas':
            return jsonify({
                'ideas': ['Resume Analyzer App', 'Job Matching Platform', 'AI Interview Coach']
            })

        elif feature_type == 'keyword_optimizer':
            return jsonify({
                'keywords': ['machine learning', 'python', 'data analysis', 'cloud']
            })

        else:
            return jsonify({'error': 'Unknown feature type'}), 400

    except Exception as e:
        app.logger.error(f"Error analyzing feature: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
"""
Web server for the ADK Triage Agent
This creates a simple web interface to interact with the agent.
"""
from flask import Flask, render_template, request, jsonify
from agent import TriageAgent
import os
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the agent
agent = TriageAgent()

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes."""
    return jsonify({
        'status': 'healthy',
        'service': 'adk-triage-agent'
    }), 200

@app.route('/readiness')
def readiness():
    """Readiness check endpoint for Kubernetes."""
    try:
        # Check if agent is initialized
        if agent and agent.client:
            return jsonify({'status': 'ready'}), 200
        else:
            return jsonify({'status': 'not ready'}), 503
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files')
def list_files():
    """List available XML files."""
    files = agent.list_files()
    return jsonify(files)

@app.route('/api/start-chat', methods=['POST'])
def start_chat():
    """Start a new chat session for a submission."""
    data = request.json
    filename = data['filename']
    
    # Read XML file
    filepath = os.path.join('inputs', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            xml_content = f.read()
    except Exception as e:
        return jsonify({'error': f'Could not read file: {e}'}), 400
    
    submission_id = filename.replace('.xml', '')
    result = agent.start_chat_session(submission_id, xml_content)
    
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the agent."""
    data = request.json
    submission_id = data['submission_id']
    message = data['message']
    
    try:
        response = agent.send_message(submission_id, message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/suggest-risk', methods=['POST'])
def suggest_risk():
    """Get AI-powered risk assessment suggestion."""
    data = request.json
    submission_id = data['submission_id']
    
    try:
        suggestion = agent.suggest_risk_assessment(submission_id)
        return jsonify({'suggestion': suggestion})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/confirm', methods=['POST'])
def confirm():
    """Confirm and save the risk assessment."""
    data = request.json
    submission_id = data['submission_id']
    risk_level = data['risk_level']
    notes = data.get('notes', '')
    
    try:
        output_file = agent.confirm_risk_assessment(submission_id, risk_level, notes)
        return jsonify({'output_file': output_file, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error confirming assessment: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logger.info(f"Starting ADK Triage Agent Web Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

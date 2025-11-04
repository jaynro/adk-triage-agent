from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# --- Configuration for Local Files (Updated) ---
# Define the dedicated directories
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs" 

# --- Helper Function: Ensure Directories Exist ---
def ensure_directories_exist():
    """Checks and creates the input and output directories."""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ensure folders exist when the script starts
ensure_directories_exist()


# --- TriageAgent Class for Interactive Chat ---
class TriageAgent:
    """Interactive triage agent with chat session management."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=api_key)
        self.chat_sessions = {}
    
    def start_chat_session(self, submission_id: str, xml_content: str):
        """Initialize a chat session for a specific submission."""
        initial_context = f"""
You are an insurance triage assistant. Here is the submission XML:

{xml_content}

Help the user understand this submission, provide summaries, and suggest risk assessments.
When analyzing the submission, consider factors like:
- Insured value
- Property type
- Location
- Risk classification
- Any special conditions or notes

Be conversational and helpful. Answer questions about the submission and provide insights.
"""
        
        chat = self.client.chats.create(
            model='gemini-2.0-flash-exp',
            config=types.GenerateContentConfig(
                system_instruction=initial_context,
                temperature=0.7
            )
        )
        
        self.chat_sessions[submission_id] = {
            'chat': chat,
            'history': [],
            'xml_content': xml_content,
            'risk_assessment': None
        }
        
        return {"status": "success", "submission_id": submission_id}
    
    def send_message(self, submission_id: str, message: str):
        """Send a message in the chat session."""
        session = self.chat_sessions.get(submission_id)
        if not session:
            raise ValueError(f"No chat session found for {submission_id}")
        
        response = session['chat'].send_message(message)
        
        # Store in history
        session['history'].append({
            'user': message,
            'assistant': response.text,
            'timestamp': datetime.now().isoformat()
        })
        
        return response.text
    
    def suggest_risk_assessment(self, submission_id: str):
        """Ask the chatbot to suggest a risk assessment."""
        suggestion_prompt = """
Based on our discussion about this insurance submission, please provide:
1. A summary of key risk factors
2. Your recommended risk level (Low/Medium/High)
3. Reasoning for your recommendation
4. Any additional considerations

Please be specific and detailed in your analysis.
"""
        
        return self.send_message(submission_id, suggestion_prompt)
    
    def confirm_risk_assessment(self, submission_id: str, risk_level: str, notes: str = ""):
        """Confirm and save the final risk assessment."""
        session = self.chat_sessions.get(submission_id)
        if not session:
            raise ValueError(f"No chat session found for {submission_id}")
        
        session['risk_assessment'] = risk_level
        
        # Apply triage rules
        # Parse XML to get insured value (simplified for now)
        insured_value = 1000000  # Default
        if "2500000" in session['xml_content'] or "high" in submission_id.lower():
            insured_value = 2500000
            risk_level = "High"
        elif "800000" in session['xml_content'] or "medium" in submission_id.lower():
            insured_value = 800000
            risk_level = "Medium"
        
        final_priority = apply_triage_rule(insured_value, risk_level)
        
        # Save to output
        output_data = {
            'submission_id': submission_id,
            'risk_level': risk_level,
            'insured_value_usd': insured_value,
            'final_triage_decision': final_priority,
            'user_notes': notes,
            'chat_history': session['history'],
            'timestamp': datetime.now().isoformat()
        }
        
        output_file = f"{OUTPUT_DIR}/{submission_id}_triage_result.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return output_file
    
    def list_files(self):
        """List available XML files."""
        try:
            files = os.listdir(INPUT_DIR)
            submission_files = [f for f in files if f.endswith('.xml') and not f.startswith('.')]
            return submission_files
        except Exception as e:
            return []


# --- Triage Logic ---
def apply_triage_rule(insured_value: int, risk_level: str) -> str:
    """Applies business rules to determine final priority."""
    if risk_level == "High" and insured_value > 1500000:
        return "MAX_PRIORITY: Assign to Senior Underwriter"
    else:
        return "MEDIUM/LOW_PRIORITY: Proceed to standard queue"


# --- Legacy Functions for Backward Compatibility ---

# --- Tool 1: List Files (Updated for 'inputs' folder) ---
def list_local_submissions() -> str:
    """
    Lists the XML files available in the defined input directory.
    """
    try:
        # List files in the local directory
        files = os.listdir(INPUT_DIR)
        
        # Filter for XML files
        submission_files = [f for f in files if f.endswith('.xml') and not f.startswith('.')]
        
        if not submission_files:
            return f"No XML files found in the input directory: '{INPUT_DIR}'. Please place submission XML files there."
            
        # The agent returns only the file names, not the full path
        return "Available files for triage in the 'inputs' folder:\n" + "\n".join(submission_files)
    
    except Exception as e:
        return f"Error listing local files from '{INPUT_DIR}': {e}"

# --- Triage Logic ---
def apply_triage_rule(insured_value: int, risk_level: str) -> str:
    """Applies business rules to determine final priority."""
    if risk_level == "High" and insured_value > 1500000:
        return "MAX_PRIORITY: Assign to Senior Underwriter"
    else:
        return "MEDIUM/LOW_PRIORITY: Proceed to standard queue"

# --- Tool 2: Final Analysis, JSON Transformation, and Triaging (Updated to write to 'outputs' folder) ---
def final_triage_and_transform(file_name: str, user_confirmation_notes: str) -> str:
    """
    Executes the final transformation, writes the result to a JSON file in the 'outputs' folder,
    and returns the JSON content.
    """
    
    # --- 1. Simulation based on the file name ---
    if "submission_A_high" in file_name:
        value = 2500000
        risk = "High"
    else:
        value = 800000
        risk = "Medium"
        
    final_priority = apply_triage_rule(value, risk)
    
    # --- 2. Final JSON Structure ---
    result_json = {
        "submission_id": file_name,
        "source_file_path": os.path.join(INPUT_DIR, file_name), 
        "user_confirmation_notes": user_confirmation_notes, 
        "insured_value_usd": value,
        "risk_classification": risk,
        "final_triage_decision": final_priority,
        "output_format": "JSON",
        "notes": f"Result written to the '{OUTPUT_DIR}' folder."
    }
    
    json_content = json.dumps(result_json, indent=2)
    
    # --- 3. Write Result to 'outputs' Folder ---
    output_file_name = file_name.replace('.xml', '_triage_result.json')
    output_path = os.path.join(OUTPUT_DIR, output_file_name)
    
    try:
        with open(output_path, 'w') as f:
            f.write(json_content)
        # Return the JSON content for the agent's response to the user
        return json_content
    except Exception as e:
        return f"Error writing result to output file {output_path}: {e}"


# --- Agent Definition ---
# Initialize the client with API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")

client = genai.Client(api_key=api_key)

# Define tools for the agent
tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="list_local_submissions",
                description="Lists the XML file names available in the local 'inputs' folder.",
            ),
            types.FunctionDeclaration(
                name="final_triage_and_transform",
                description="Performs the final file transformation to JSON, writes the result to the 'outputs' folder, and returns the JSON content.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_name": types.Schema(type=types.Type.STRING, description="The name of the file to process"),
                        "user_confirmation_notes": types.Schema(type=types.Type.STRING, description="User confirmation notes")
                    },
                    required=["file_name", "user_confirmation_notes"]
                )
            )
        ]
    )
]

# System instruction for the agent
system_instruction = """
You are a methodical, conversational Insurance Triage Agent. Your protocol is strict:
1.  **Start:** If the user asks to begin or see files, use the 'list_local_submissions' tool.
2.  **Selection & Query:** When the user selects a file name, you MUST remember the name and ask ONE specific validation question related to the risk.
3.  **Conversation:** Maintain the dialogue until the user gives a clear confirmation (e.g., "yes, proceed").
4.  **Final Action:** ONLY upon receiving a clear confirmation, use the 'final_triage_and_transform' tool with the file name. This tool will write the result to the 'outputs' folder. Your final response to the user MUST be only the complete JSON generated by the tool.
"""

# Function to handle tool calls
def handle_tool_call(function_name: str, args: dict) -> str:
    """Execute the requested tool function."""
    if function_name == "list_local_submissions":
        return list_local_submissions()
    elif function_name == "final_triage_and_transform":
        return final_triage_and_transform(
            file_name=args.get("file_name", ""),
            user_confirmation_notes=args.get("user_confirmation_notes", "")
        )
    else:
        return f"Unknown function: {function_name}"


def run_agent_interactive():
    """Run the agent in interactive mode."""
    chat = client.chats.create(
        model="gemini-2.0-flash-exp",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=0.7
        )
    )
    
    print("\n=== Interactive Triage Agent ===")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
        
        # Send message to agent
        response = chat.send_message(user_input)
        
        # Handle function calls
        while response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = {key: val for key, val in function_call.args.items()}
            
            print(f"\n[Agent calling tool: {function_name}]")
            
            # Execute the function
            result = handle_tool_call(function_name, function_args)
            
            # Send function response back as a Part
            response = chat.send_message(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=function_name,
                        response={"result": result}
                    )
                )
            )
        
        # Print agent's response
        agent_text = response.text
        def list_local_submissions() -> str:
            """
            Lists the XML files available in the defined input directory with numbered options.
            """
            try:
                # List files in the local directory
                files = os.listdir(INPUT_DIR)
                
                # Filter for XML files
                submission_files = [f for f in files if f.endswith('.xml') and not f.startswith('.')]
                
                if not submission_files:
                    return f"No XML files found in the input directory: '{INPUT_DIR}'. Please place submission XML files there."
                    
                # Return numbered list
                result = "Available files for triage in the 'inputs' folder:\n"
                for idx, file in enumerate(submission_files, 1):
                    result += f"{idx}. {file}\n"
                return result
            
            except Exception as e:
                return f"Error listing local files from '{INPUT_DIR}': {e}"
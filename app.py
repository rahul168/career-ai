"""
Career AI Application

This module provides a Gradio-based chat interface that acts as an AI assistant
representing a candidate's professional profile. It uses GenerativeAI to answer
questions about the candidate's career, background, skills, and experience based
on their LinkedIn profile and project information.

The application supports:
- Interactive chat interface via Gradio
- Function calling for recording user details and unknown questions
- Integration with Pushover for notifications
- PDF parsing for LinkedIn profile and projects data
"""

from dotenv import load_dotenv
from openai import OpenAI
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List
import requests
from pypdf import PdfReader
import gradio as gr
import config

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Constants
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
RESOURCES_DIR = Path("./resources")
PROFILE_PDF = RESOURCES_DIR / "ProfileLinkedIn.pdf"
PROJECTS_PDF = RESOURCES_DIR / "ProjectsLinkedIn.pdf"
SUMMARY_FILE = RESOURCES_DIR / "summary.txt"

load_dotenv(override=True)

def push(text: str) -> None:
    """
    Send a notification message via Pushover API.
    
    Args:
        text: The message text to send as a notification.
    
    Note:
        Requires PUSHOVER_TOKEN and PUSHOVER_USER environment variables to be set.
    
    Raises:
        requests.RequestException: If the API request fails.
    """
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    
    if not token or not user:
        logger.warning("Pushover credentials not set, skipping notification")
        return
    
    try:
        response = requests.post(
            PUSHOVER_API_URL,
            data={"token": token, "user": user, "message": text},
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to send Pushover notification: {e}")


def record_user_details(email: str, name: str = "Name not provided", notes: str = "Notes not provided") -> Dict[str, str]:
    """
    Record user contact details and send a notification.
    
    This function is called by the AI assistant when a user provides their email
    address or expresses interest in being contacted.
    
    Args:
        email: The user's email address (required).
        name: The user's name, defaults to "Name not provided".
        notes: Additional context about the conversation, defaults to "not provided".
    
    Returns:
        A dictionary with a "recorded" key set to "ok" indicating successful recording.
    """
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question: str) -> Dict[str, str]:
    """
    Record a question that the AI assistant couldn't answer.
    
    This function is called by the AI assistant when it encounters a question
    it cannot answer, allowing for tracking and improvement of the knowledge base.
    
    Args:
        question: The question that couldn't be answered.
    
    Returns:
        A dictionary with a "recorded" key set to "ok" indicating successful recording.
    """
    push(f"Recording unanswered question: {question}")
    return {"recorded": "ok"}

# OpenAI function calling tool definition for recording user contact details
record_user_details_json = {
    "type": "function",
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

# OpenAI function calling tool definition for recording unanswered questions
record_unknown_question_json = {
    "type": "function",
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# List of available tools for OpenAI function calling
tools = [record_user_details_json, record_unknown_question_json]


class CareerAI:
    """
    Career AI Chat Assistant
    
    This class manages the chat interface and interactions with OpenAI's API
    to answer questions about a candidate's professional background. It loads
    profile information from PDF files and text summaries, and maintains
    conversation context while handling function calls.
    
    Attributes:
        gpt_responder_client: OpenAI client instance for chat responses.
        name: The candidate's name.
        linkedin_profile: Extracted text from the LinkedIn profile PDF.
        linkedin_projects: Extracted text from the LinkedIn projects PDF.
        summary: Summary text loaded from summary.txt.
        gpt_responder_model: Model name for the responder (from config).
        gpt_validator_model: Model name for the validator (from config).
    """
    
    def __init__(self):
        """
        Initialize the CareerAI instance.
        
        Loads candidate information from:
        - ProfileLinkedIn.pdf: LinkedIn profile data
        - ProjectsLinkedIn.pdf: LinkedIn projects data
        - summary.txt: Text summary of the candidate's background
        
        Initializes OpenAI client and loads model configurations from config.
        
        Raises:
            FileNotFoundError: If required resource files are missing.
            ValueError: If resource files cannot be read.
        """
        self.gpt_responder_client = OpenAI()
        self.name = config.CANDIDATE_NAME
        self.linkedin_profile = self._extract_pdf_text(PROFILE_PDF)
        self.linkedin_projects = self._extract_pdf_text(PROJECTS_PDF)
        self.summary = self._load_text_file(SUMMARY_FILE)
        self.gpt_responder_model = config.GPT_RESPONDER_MODEL
        self.gpt_validator_model = config.GPT_VALIDATOR_MODEL
    
    @staticmethod
    def _extract_pdf_text(pdf_path: Path) -> str:
        """
        Extract all text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
        
        Returns:
            Concatenated text from all pages of the PDF.
        
        Raises:
            FileNotFoundError: If the PDF file doesn't exist.
            ValueError: If the PDF cannot be read.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = PdfReader(str(pdf_path))
            return "".join(
                page.extract_text() 
                for page in reader.pages 
                if page.extract_text()
            )
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            raise ValueError(f"Failed to extract text from {pdf_path}") from e
    
    @staticmethod
    def _load_text_file(file_path: Path) -> str:
        """
        Load text content from a file.
        
        Args:
            file_path: Path to the text file.
        
        Returns:
            Content of the text file.
        
        Raises:
            FileNotFoundError: If the file doesn't exist.
            IOError: If the file cannot be read.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")
        
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise IOError(f"Failed to read {file_path}") from e

    def handle_tool_call(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute function calls requested by the AI assistant.
        
        Processes tool calls from OpenAI's response, executes the corresponding
        functions, and returns the results in the format expected by OpenAI.
        
        Args:
            tool_calls: List of tool call objects from OpenAI response.
        
        Returns:
            List of dictionaries containing function call outputs with call IDs,
            formatted for inclusion in the conversation history.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.name            
            arguments = json.loads(tool_call.arguments)
            logger.info(f"Tool called: {tool_name}")
            tool_func = globals().get(tool_name)            
            result = tool_func(**arguments)            
            results.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result)
            })
        return results
    
    def system_prompt(self) -> str:
        """
        Generate the system prompt for the AI assistant.
        
        Creates a comprehensive system prompt that includes the candidate's name,
        summary, LinkedIn profile, and projects information.
        
        Returns:
            The formatted system prompt string.
        """
        return config.get_responder_system_prompt(self.name, self.summary, self.linkedin_profile, self.linkedin_projects)
    
    def history_content(self, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Convert Gradio chat history format to OpenAI message format.
        
        Transforms the Gradio chat history (which uses a nested structure)
        into the flat message format expected by OpenAI's API.
        
        Args:
            history: Gradio chat history list with nested content structure.
        
        Returns:
            List of message dictionaries with "role" and "content" keys.
        """
        return [
            {"role": message["role"], "content": message["content"][0]["text"]}
            for message in history
        ]

    def chat(self, user_input: str, history: List[Dict[str, Any]]) -> str:
        """
        Process a chat message and generate a response.
        
        This is the main chat handler that:
        1. Builds the conversation context with system prompt and history
        2. Sends the request to OpenAI with function calling enabled
        3. Handles any function calls iteratively until a final response is generated
        4. Returns the text response to display in the chat interface
        
        Args:
            user_input: The user's current message/input.
            history: The conversation history from Gradio (previous messages).
        
        Returns:
            The AI assistant's text response to display to the user.
        
        Raises:
            Exception: If the OpenAI API call fails or returns an invalid response.
        """
        # Build the full conversation context: system prompt + history + current input
        messages = [{"role": "system", "content": self.system_prompt()}] + self.history_content(history) + [{"role": "user", "content": user_input}]
        
        # Loop until we get a final text response (no more function calls)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0        
        while iteration < max_iterations:
            try:
                response = self.gpt_responder_client.responses.create(model=self.gpt_responder_model, input=messages, tools=tools)
                messages.extend(response.output)                
                # Check if the response includes function calls
                tool_calls = [ item for item in response.output if item.type == "function_call" ]                
                if tool_calls:
                    # Execute function calls and add results to conversation
                    results = self.handle_tool_call(tool_calls)
                    messages.extend(results)
                    iteration += 1
                else:
                    # No more function calls, we have the final response
                    return response.output_text                    
            except Exception as e:
                logger.error(f"Error in chat processing: {e}")
                return f"I apologize, but I encountered an error: {str(e)}"
        
        logger.warning("Maximum iterations reached in chat loop")
        return "I apologize, but I'm having trouble processing your request. Please try again."
    

def main() -> None:
    """
    Main entry point for the application.
    
    Initializes the CareerAI instance and launches the Gradio chat interface.
    The interface will be accessible via a web browser at the URL shown in the console.
    """
    try:
        career_responder = CareerAI()
        logger.info("CareerAI initialized successfully")
        gr.ChatInterface(career_responder.chat, fill_height=True).launch()    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        

if __name__ == "__main__":
    main()

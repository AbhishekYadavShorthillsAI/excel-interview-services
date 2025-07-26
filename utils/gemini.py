import json
import logging
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ['GEMINI_API_KEY'])


def _get_system_instruction(messages):
    for message in messages:
        if message['role'] == 'system':
            return message['content']
    else:
        return 'You are an AI based Assistant.'
    
def _prepare_gemini_prompt(messages):
    """
    Prepare history and current message for Gemini.
    This now handles the full conversation history including tool calls.
    """
    history = list()    
    current_message = None
    
    # Find the last user message (this will be the current message)
    user_messages = [msg for msg in messages if msg['role'] == 'user']
    if user_messages:
        current_message = user_messages[-1]['content']
    
    # Build history excluding system messages and the last user message
    for i, message in enumerate(messages):
        if message['role'] == 'system':
            continue  # Skip system messages in history
        elif message['role'] == 'assistant':
            # Check if this is a tool call or regular response
            if message.get('tool_calls'):
                # This is a tool call response
                tool_calls = message['tool_calls']
                parts = []
                for tool_call in tool_calls:
                    # Create function call part
                    function_call = genai.protos.FunctionCall(
                        name=tool_call['name'],
                        args=tool_call['args']
                    )
                    parts.append(genai.protos.Part(function_call=function_call))
                
                history.append({
                    'role': 'model',
                    'parts': parts
                })
            else:
                # Regular assistant response
                history.append({
                    'role': 'model',
                    'parts': [message['content']]
                })
        elif message['role'] == 'tool':
            # This is a tool result
            function_response = genai.protos.FunctionResponse(
                name=message['tool_name'],
                response={"result": message['content']}
            )
            history.append({
                'role': 'user',
                'parts': [genai.protos.Part(function_response=function_response)]
            })
        elif message['role'] == 'user':
            # Only add user messages to history if they're not the last user message
            if message['content'] != current_message:
                history.append({
                    'role': 'user',
                    'parts': [message['content']]
                })
            # If this is the last user message in the list, don't add it to history
            elif i == len(messages) - 1:
                continue
            else:
                history.append({
                    'role': 'user',
                    'parts': [message['content']]
                })
            
    return history, current_message


class GeminiClient:
    def __init__(self, model="gemini-2.5-pro", temperature=0.0, max_tokens=1024):
        self.model_id = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        
    async def invoke(self, messages):
        """
        Simple invocation without tools.
        messages: List of conversation messages from client
        Returns: (response_text, updated_messages)
        """
        logging.info(f"LLM call through Gemini {self.model_id} (step 0)")
        
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        
        system_message = _get_system_instruction(messages)

        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=generation_config,
            system_instruction=system_message,
        )
        
        history, user_message = _prepare_gemini_prompt(messages=messages)
        
        chat_session = model.start_chat(history=history)
        
        logging.info(f"LLM call chat session created (step 1)")
        
        response = await chat_session.send_message_async(user_message)
        
        # Add assistant response to messages
        updated_messages = messages + [
            {
                "role": "assistant",
                "content": response.text
            }
        ]
        
        logging.info(f"LLM Call Response through Gemini {self.model_id}: {response.text}")
        return response.text, updated_messages
    

    async def invoke_tools(self, messages, tools):
        """
        Invocation with tools support.
        messages: List of conversation messages from client
        Returns: (response_text, updated_messages)
        """
        logging.info(f"LLM call through Gemini {self.model_id} (step 0)")
        
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": 8192,
        }
        
        system_message = _get_system_instruction(messages)

        model = genai.GenerativeModel(
            model_name=self.model_id,
            generation_config=generation_config,
            system_instruction=system_message,
            tools=tools
        )
        
        history, user_message = _prepare_gemini_prompt(messages=messages)
        
        # Start chat session with the provided history
        chat_session = model.start_chat(history=history)
        
        logging.info(f"LLM call chat session created with {len(history)} history messages")
        
        # Send the current user message
        response = await chat_session.send_message_async(user_message)

        # Create a serializable response wrapper that maintains compatibility
        class SerializableResponse:
            def __init__(self, original_response):
                self._original = original_response
                # Extract the candidates data in a serializable format
                self.candidates = []
                for candidate in original_response.candidates:
                    candidate_data = type('obj', (object,), {})()
                    candidate_data.content = type('obj', (object,), {})()
                    candidate_data.content.parts = []
                    
                    for part in candidate.content.parts:
                        part_data = type('obj', (object,), {})()
                        if hasattr(part, 'function_call') and part.function_call:
                            # Convert function call to serializable format
                            part_data.function_call = type('obj', (object,), {})()
                            part_data.function_call.name = part.function_call.name
                            part_data.function_call.args = dict(part.function_call.args)
                        elif hasattr(part, 'text'):
                            part_data.text = part.text
                        candidate_data.content.parts.append(part_data)
                    
                    self.candidates.append(candidate_data)
        
        serializable_response = SerializableResponse(response)
        
        # Create a serializable chat session wrapper
        class SerializableChatSession:
            def __init__(self, original_session):
                self._original = original_session
            
            async def send_message_async(self, message):
                response = await self._original.send_message_async(message)
                # Create a simple serializable response object with just the text
                class SimpleResponse:
                    def __init__(self, text):
                        self.text = text
                return SimpleResponse(response.text)
        
        serializable_chat_session = SerializableChatSession(chat_session)
        
        return serializable_response, serializable_chat_session

from utils.gemini import GeminiClient
from utils.prompts import SYSTEM_PROMPT_ORCHESTRATOR, SYSTEM_PROMPT_QUESTION_GENERATION
from generator.handler.common import save_questions_to_db
import google.generativeai as genai
from google.ai.generativelanguage import FunctionDeclaration, Tool
from utils.tools import generate_and_save_tool, generate_web_research_tool
from utils.perplexcity import PerplexityClient
import json
import logging

def create_simple_message(role, content, tool_calls=None, tool_name=None):
    """Create a simple, serializable message structure"""
    message = {
        "role": str(role),
        "content": str(content)
    }
    
    if tool_calls:
        message["tool_calls"] = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                simple_call = {
                    "name": str(tool_call.get("name", "")),
                    "args": tool_call.get("args", {})  # Keep the properly converted args
                }
                message["tool_calls"].append(simple_call)
    
    if tool_name:
        message["tool_name"] = str(tool_name)
    
    return message

def convert_proto_to_dict(obj):
    """Convert Google AI proto objects to regular Python dictionaries"""
    if hasattr(obj, '_pb'):
        # This is a proto object, try to convert it
        try:
            # Convert proto to dict by accessing the underlying data
            if hasattr(obj, 'items'):
                # It's a map-like object
                return {str(k): convert_proto_to_dict(v) for k, v in obj.items()}
            elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                # It's a list-like object
                return [convert_proto_to_dict(item) for item in obj]
            else:
                return str(obj)
        except Exception:
            return str(obj)
    elif isinstance(obj, dict):
        return {str(k): convert_proto_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_proto_to_dict(item) for item in obj]
    else:
        return obj

async def process_admin_conversation(history: list, query: str):
    
    client = GeminiClient()

    messages = [{"role": "system", "content": SYSTEM_PROMPT_ORCHESTRATOR}]

    # Add history
    messages.extend(history)

    messages.append({
        "role": "user",
        "content": query
    })

    try:
        response, chat_session = await client.invoke_tools(messages, tools=[generate_and_save_tool, generate_web_research_tool])

        has_function_calls = (
            hasattr(response.candidates[0].content.parts[0], 'function_call') and 
            response.candidates[0].content.parts[0].function_call
        )

        if has_function_calls:
            function_call = response.candidates[0].content.parts[0].function_call
        else:
            function_call = None

        # Check if model wants to call a function
        if function_call:
            tool_call = function_call
            
            # Properly convert protobuf args to avoid serialization issues
            converted_args = convert_proto_to_dict(tool_call.args)
            tool_call_message = {
                                    "role": "assistant",
                                    "tool_calls": [
                                        {
                                            "name": tool_call.name,
                                            "args": converted_args
                                        }
                                    ]
                                }
            
            messages.append(tool_call_message)
            
            if tool_call.name == "generate_and_save":
                # Execute the function with new multi-topic structure
                topic_specifications = converted_args.get("topic_specifications", [])
                
                result = await generate_and_save_multi_topic(topic_specifications)
                logging.info(f"Multi-topic generation result: {result}")

                # Add tool result to history
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_call.name,
                        "content": result
                    }
                )
            
            elif tool_call.name == "perplexcity_web_research_and_save":
                # Execute the web research function with multi-topic structure
                topic_specifications = converted_args.get("topic_specifications", [])
                
                result = await generate_web_research_multi_topic(topic_specifications)
                logging.info(f"Web research generation result: {result}")

                # Add tool result to history
                messages.append({
                        "role": "tool",
                        "tool_name": tool_call.name,
                        "content": result
                    })
            
            function_response_part = genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=tool_call.name,
                    response={"result": result}
                )
            )

            # Send function response back to get final answer
            final_response = await chat_session.send_message_async([function_response_part])

            response_text = final_response.text

            messages.append({"role": "assistant", "content": response_text})

        else:
            # No tool call, just add regular response
            response_text = response.candidates[0].content.parts[0].text
            messages.append({"role": "assistant", "content": response_text})
        
        return messages

    except Exception as e:
        logging.error(f"Error in process_admin_conversation: {e}")
        # Return a clean error message
        error_message = {
            "role": "assistant", 
            "content": f"I encountered an error: {str(e)}. Please try again."
        }
        return history + [error_message]


async def generate_and_save_multi_topic(topic_specifications: list):
    """Generate interview questions for multiple topics with individual specifications"""
    
    try:
        if not topic_specifications:
            return "No topic specifications provided."
        
        client = GeminiClient()
        
        # Build the formatted request for the AI
        formatted_request = "Topic Specifications:\n"
        total_questions = 0
        
        for spec in topic_specifications:
            topic = spec.get("topic", "")
            mcq_count = int(float(spec.get("mcq_count", 0)))  # Handle float values from proto
            descriptive_count = int(float(spec.get("descriptive_count", 0)))  # Handle float values from proto
            
            formatted_request += f"- Topic: {topic}\n"
            formatted_request += f"  MCQ Count: {mcq_count}\n"
            formatted_request += f"  Descriptive Count: {descriptive_count}\n"
            
            total_questions += mcq_count + descriptive_count

        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT_QUESTION_GENERATION
        }]

        messages.append({
            "role": "user",
            "content": formatted_request
        })

        response_text, _ = await client.invoke(messages)
        
        # Parse the JSON response from the AI
        try:

            l_idx = response_text.find("[")
            r_idx = response_text.rfind("]")
            if l_idx != -1 and r_idx != -1:
                response_text = response_text[l_idx : r_idx+1]
                
            questions_data = json.loads(response_text)
            
            # Validate that it's a list
            if not isinstance(questions_data, list):
                raise ValueError("Expected a list of questions")
            
            # Process each question to ensure correct format
            processed_questions = []
            topic_counts = {}
            
            for q in questions_data:
                topic_name = q.get("topic", "Unknown")
                processed_question = {
                    "question": q.get("question", ""),
                    "answer": q.get("answer", ""),
                    "question_type": q.get("type", "").lower(),  # Normalize type
                    "options": q.get("options") if q.get("options") else None,
                    "tag": topic_name  # Use the topic name as tag
                }
                processed_questions.append(processed_question)
                
                # Count questions by topic for validation
                if topic_name not in topic_counts:
                    topic_counts[topic_name] = {"mcq": 0, "descriptive": 0}
                topic_counts[topic_name][processed_question["question_type"]] += 1
            
            # Validate question counts match specifications
            validation_errors = []
            for spec in topic_specifications:
                topic = spec.get("topic", "")
                expected_mcq = int(float(spec.get("mcq_count", 0)))
                expected_desc = int(float(spec.get("descriptive_count", 0)))
                
                actual_counts = topic_counts.get(topic, {"mcq": 0, "descriptive": 0})
                if actual_counts["mcq"] != expected_mcq:
                    validation_errors.append(f"Topic '{topic}': Expected {expected_mcq} MCQ, got {actual_counts['mcq']}")
                if actual_counts["descriptive"] != expected_desc:
                    validation_errors.append(f"Topic '{topic}': Expected {expected_desc} descriptive, got {actual_counts['descriptive']}")
            
            # Save to database
            success = await save_questions_to_db(processed_questions)
            
            if success:
                # Build success message with breakdown
                topic_summary = []
                for spec in topic_specifications:
                    topic = spec.get("topic", "")
                    mcq_count = int(float(spec.get("mcq_count", 0)))
                    descriptive_count = int(float(spec.get("descriptive_count", 0)))
                    topic_summary.append(f"{topic} ({mcq_count} MCQ, {descriptive_count} descriptive)")
                
                result_message = f"Successfully generated and saved {len(processed_questions)} questions across {len(topic_specifications)} topics:\n"
                result_message += "\n".join(f"• {summary}" for summary in topic_summary)
                
                if validation_errors:
                    result_message += f"\n\nNote: Some question counts may not match exactly due to AI generation variance:\n"
                    result_message += "\n".join(f"• {error}" for error in validation_errors)
                
                return result_message
            else:
                return "Questions were generated but there was an error saving them to the database."
                
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI response as JSON: {e}")
            logging.error(f"Raw response: {response_text}")
            return "I generated the questions, but there was an error processing the response format."
        except Exception as e:
            logging.error(f"Error processing questions: {e}")
            return "There was an error processing the generated questions."
            
    except Exception as e:
        logging.error(f"Error in generate_and_save_multi_topic: {e}")
        return f"I encountered an error while generating questions: {str(e)}"


async def generate_web_research_multi_topic(topic_specifications: list):
    """Generate interview questions for multiple topics using web research with Perplexity AI"""
    
    try:
        if not topic_specifications:
            return "No topic specifications provided."
        
        perplexity_client = PerplexityClient()
        gemini_client = GeminiClient()
        
        # Research each topic using Perplexity to get current information
        researched_topics = []
        
        for spec in topic_specifications:
            topic = spec.get("topic", "")
            mcq_count = int(float(spec.get("mcq_count", 0)))
            descriptive_count = int(float(spec.get("descriptive_count", 0)))
            
            # Create research query for Perplexity
            research_query = f"Latest trends, developments, and important concepts in {topic}. Include recent updates, best practices, and industry standards."
            
            try:
                # Get web research from Perplexity
                research_content = await perplexity_client.invoke(research_query)
                
                researched_topics.append({
                    "topic": topic,
                    "mcq_count": mcq_count,
                    "descriptive_count": descriptive_count,
                    "research_content": research_content
                })
                
                logging.info(f"Completed web research for topic: {topic}")
                
            except Exception as e:
                logging.error(f"Error researching topic '{topic}': {e}")
                # Fallback to basic topic without research
                researched_topics.append({
                    "topic": topic,
                    "mcq_count": mcq_count,
                    "descriptive_count": descriptive_count,
                    "research_content": f"Unable to fetch latest information for {topic}. Please generate questions based on general knowledge."
                })
        
        # Build the formatted request for Gemini AI with research context
        formatted_request = "Generate interview questions based on the following web research findings:\n\n"
        total_questions = 0
        
        for spec in researched_topics:
            topic = spec.get("topic", "")
            mcq_count = spec.get("mcq_count", 0)
            descriptive_count = spec.get("descriptive_count", 0)
            research_content = spec.get("research_content", "")
            
            formatted_request += f"Topic: {topic}\n"
            formatted_request += f"MCQ Count: {mcq_count}\n"
            formatted_request += f"Descriptive Count: {descriptive_count}\n"
            formatted_request += f"Recent Research Findings:\n{research_content}\n"
            formatted_request += "-" * 50 + "\n"
            
            total_questions += mcq_count + descriptive_count

        formatted_request += f"\nPlease generate questions that incorporate the latest information from the web research above."

        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT_QUESTION_GENERATION
        }]

        messages.append({
            "role": "user",
            "content": formatted_request
        })

        response_text, _ = await gemini_client.invoke(messages)
        
        # Parse the JSON response from the AI
        try:
            l_idx = response_text.find("[")
            r_idx = response_text.rfind("]")
            if l_idx != -1 and r_idx != -1:
                response_text = response_text[l_idx : r_idx+1]
                
            questions_data = json.loads(response_text)
            
            # Validate that it's a list
            if not isinstance(questions_data, list):
                raise ValueError("Expected a list of questions")
            
            # Process each question to ensure correct format
            processed_questions = []
            topic_counts = {}
            
            for q in questions_data:
                topic_name = q.get("topic", "Unknown")
                processed_question = {
                    "question": q.get("question", ""),
                    "answer": q.get("answer", ""),
                    "question_type": q.get("type", "").lower(),  # Normalize type
                    "options": q.get("options") if q.get("options") else None,
                    "tag": f"{topic_name} (Web Research)"  # Add web research indicator to tag
                }
                processed_questions.append(processed_question)
                
                # Count questions by topic for validation
                if topic_name not in topic_counts:
                    topic_counts[topic_name] = {"mcq": 0, "descriptive": 0}
                topic_counts[topic_name][processed_question["question_type"]] += 1
            
            # Save to database
            success = await save_questions_to_db(processed_questions)
            
            if success:
                # Build success message with breakdown
                topic_summary = []
                for spec in topic_specifications:
                    topic = spec.get("topic", "")
                    mcq_count = int(float(spec.get("mcq_count", 0)))
                    descriptive_count = int(float(spec.get("descriptive_count", 0)))
                    topic_summary.append(f"{topic} ({mcq_count} MCQ, {descriptive_count} descriptive)")
                
                result_message = f"Successfully generated and saved {len(processed_questions)} questions based on web research across {len(topic_specifications)} topics:\n"
                result_message += "\n".join(f"• {summary}" for summary in topic_summary)
                result_message += f"\n\nThese questions incorporate the latest information from web research and current industry trends."
                
                return result_message
            else:
                return "Questions were generated using web research but there was an error saving them to the database."
                
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI response as JSON: {e}")
            logging.error(f"Raw response: {response_text}")
            return "I generated the questions using web research, but there was an error processing the response format."
        except Exception as e:
            logging.error(f"Error processing web research questions: {e}")
            return "There was an error processing the generated questions from web research."
            
    except Exception as e:
        logging.error(f"Error in generate_web_research_multi_topic: {e}")
        return f"I encountered an error while generating questions with web research: {str(e)}"


# Legacy function for backward compatibility
async def generate_and_save(query, tag, number):
    """Legacy function that converts single topic request to multi-topic format"""
    
    # Determine question type breakdown
    if tag.lower() == "mcq":
        mcq_count = number
        descriptive_count = 0
    elif tag.lower() == "descriptive":
        mcq_count = 0
        descriptive_count = number
    else:
        # For mixed or unclear types, split evenly
        mcq_count = number // 2
        descriptive_count = number - mcq_count
    
    # Convert to new format
    topic_specifications = [{
        "topic": query,
        "mcq_count": mcq_count,
        "descriptive_count": descriptive_count
    }]
    
    return await generate_and_save_multi_topic(topic_specifications)

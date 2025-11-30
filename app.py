"""
TAXBOT - Nigeria Tax Reform Intelligence Assistant
Gradio Interface for Hugging Face Spaces
"""

import gradio as gr
import requests
import os
from typing import Optional
import json

# Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
API_TIMEOUT = 30

# Store conversation history
conversation_history = []

def chat_with_taxbot(user_message: str, chat_history: list) -> tuple:
    """
    Send user message to TAXBOT backend and get response
    
    Args:
        user_message: The user's tax-related question
        chat_history: Gradio chat history
        
    Returns:
        Updated chat history with bot response
    """
    
    if not user_message.strip():
        return chat_history
    
    try:
        # Prepare request to backend
        payload = {
            "query": user_message,
            "conversation_context": conversation_history
        }
        
        # Make API call to backend
        response = requests.post(
            f"{BACKEND_API_URL}/api/chat",
            json=payload,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "I couldn't process your request. Please try again.")
            sources = data.get("sources", [])
            
            # Format response with sources if available
            if sources:
                bot_response += "\n\n📚 **Sources:**\n"
                for source in sources[:3]:  # Limit to 3 sources
                    bot_response += f"• {source}\n"
            
            # Update conversation history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })
            
        else:
            bot_response = f"⚠️ Error: {response.status_code} - Unable to reach the backend service."
            
    except requests.exceptions.ConnectionError:
        bot_response = "⚠️ Connection Error: Cannot reach the backend API. Please ensure the service is running."
    except requests.exceptions.Timeout:
        bot_response = "⏱️ Timeout: The backend service took too long to respond. Please try again."
    except Exception as e:
        bot_response = f"❌ Error: {str(e)}"
    
    # Add to chat history for Gradio display
    chat_history.append((user_message, bot_response))
    
    return chat_history


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return []


def check_backend_status() -> str:
    """Check if backend API is available"""
    try:
        response = requests.get(
            f"{BACKEND_API_URL}/health",
            timeout=5
        )
        if response.status_code == 200:
            return "✅ Backend API is connected and running"
        else:
            return f"⚠️ Backend returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to backend API. Make sure it's running."
    except Exception as e:
        return f"❌ Error checking backend: {str(e)}"


# Create Gradio Interface
with gr.Blocks(title="TAXBOT - Nigeria Tax Reform Intelligence Assistant", theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.Markdown(
        """
        # 🇳🇬 TAXBOT - Nigeria Tax Reform Intelligence Assistant
        
        Welcome! Ask me anything about Nigeria's 2025 Tax Reform Act. I'm here to help you understand tax obligations, compliance requirements, and more.
        
        **Powered by Graph-Enhanced RAG (Retrieval-Augmented Generation)**
        """
    )
    
    # Status indicator
    status = gr.Markdown(f"**Status:** {check_backend_status()}")
    
    # Chat interface
    chatbot = gr.Chatbot(
        label="Chat History",
        height=400,
        show_copy_button=True
    )
    
    # Input section
    with gr.Row():
        msg = gr.Textbox(
            label="Your Question",
            placeholder="Ask me about tax obligations, compliance deadlines, or anything related to Nigeria's tax reform...",
            lines=3,
            scale=4
        )
        submit_btn = gr.Button("Send", scale=1, variant="primary")
    
    # Control buttons
    with gr.Row():
        clear_btn = gr.Button("Clear Chat", variant="secondary")
        refresh_btn = gr.Button("Refresh Backend Status", variant="secondary")
    
    # Example questions
    gr.Examples(
        examples=[
            "What are the new tax brackets under the 2025 reform?",
            "Who is eligible for tax reliefs in Nigeria?",
            "What are the compliance deadlines for the new tax year?",
            "How does the simplified taxation for small businesses work?",
            "What documents do I need for tax registration?"
        ],
        inputs=msg,
        label="Example Questions"
    )
    
    # Information section
    with gr.Accordion("ℹ️ About TAXBOT", open=False):
        gr.Markdown(
            """
            ### About This Assistant
            
            TAXBOT (Nigeria Tax Reform Intelligence Assistant) uses advanced AI and a knowledge graph to provide accurate information about Nigeria's 2025 Tax Reform Act.
            
            **Features:**
            - 📚 Comprehensive tax guidance based on official documents
            - 🔗 Knowledge graph connecting tax concepts and regulations
            - 💡 Personalized recommendations
            - 📋 Compliance deadline alerts
            - 🎯 Multi-step guidance for complex tax scenarios
            
            **Data Source:** Official Nigeria Tax Reform Act 2025 documents
            
            **Disclaimer:** This is an AI assistant for informational purposes. For official tax advice, consult with qualified tax professionals.
            """
        )
    
    # Event handlers
    submit_btn.click(
        fn=chat_with_taxbot,
        inputs=[msg, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        outputs=msg
    )
    
    msg.submit(
        fn=chat_with_taxbot,
        inputs=[msg, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        outputs=msg
    )
    
    clear_btn.click(
        fn=clear_history,
        outputs=chatbot
    )
    
    refresh_btn.click(
        fn=lambda: f"**Status:** {check_backend_status()}",
        outputs=status
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

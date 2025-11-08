"""
Gemini AI Integration using Vertex AI
Connects to Google Cloud Vertex AI Gemini 1.5 Flash model
"""

import os
from typing import Optional, List, Dict, Any
import google.auth
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, ChatSession, Part, Content
import vertexai

class GeminiClient:
    """
    Client for interacting with Gemini 1.5 Flash model via Vertex AI
    """
    
    def __init__(
        self,
        project_id: str = None,
        location: str = "us-central1",
        model_name: str = "gemini-2.5-flash"
    ):
        """
        Initialize Gemini client
        
        Args:
            project_id: GCP project ID (if None, will use default from credentials)
            location: GCP region for Vertex AI
            model_name: Gemini model to use
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        # Initialize the model
        self.model = GenerativeModel(self.model_name)
        
        # Chat session (for conversation context)
        self.chat_session: Optional[ChatSession] = None
        
        print(f"✅ Gemini client initialized")
        print(f"   Project: {self.project_id}")
        print(f"   Location: {self.location}")
        print(f"   Model: {self.model_name}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        top_p: float = 0.95,
        top_k: int = 40
    ) -> str:
        """
        Generate text response from a prompt
        
        Args:
            prompt: Input prompt
            temperature: Creativity (0.0-1.0)
            max_output_tokens: Maximum response length
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            
        Returns:
            Generated text response
        """
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "top_p": top_p,
                "top_k": top_k
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Error generating text: {e}")
            raise
    
    def start_chat(self, context: Optional[str] = None) -> ChatSession:
        """
        Start a new chat session with optional context
        
        Args:
            context: Initial context/system message
            
        Returns:
            Chat session object
        """
        history = []
        if context:
            history = [
                Content(
                    role="user",
                    parts=[Part.from_text(context)]
                ),
                Content(
                    role="model",
                    parts=[Part.from_text("Understood. I'm ready to assist.")]
                )
            ]
        
        self.chat_session = self.model.start_chat(history=history)
        return self.chat_session
    
    def send_message(
        self,
        message: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ) -> str:
        """
        Send a message in the current chat session
        
        Args:
            message: User message
            temperature: Creativity
            max_output_tokens: Maximum response length
            
        Returns:
            Model response
        """
        if not self.chat_session:
            self.start_chat()
        
        try:
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens
            }
            
            response = self.chat_session.send_message(
                message,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            raise
    
    def analyze_esg_data(
        self,
        metric_name: str,
        data: List[Dict[str, Any]],
        metric_type: str = "emissions"
    ) -> str:
        """
        Analyze ESG data and provide insights
        
        Args:
            metric_name: Name of the metric
            data: List of data points
            metric_type: Type of metric (emissions, social, governance)
            
        Returns:
            AI-generated analysis and insights
        """
        prompt = f"""
You are an ESG (Environmental, Social, Governance) analyst expert. Analyze the following {metric_type} data for {metric_name}.

Data:
{data}

Provide a concise analysis including:
1. Key trends (improving, declining, or stable)
2. Notable patterns or anomalies
3. Actionable recommendations (2-3 specific suggestions)
4. Overall assessment

Keep the response under 200 words and focus on actionable insights.
"""
        
        return self.generate_text(prompt, temperature=0.4)
    
    def generate_esg_summary(
        self,
        emissions_data: Optional[Dict] = None,
        social_data: Optional[Dict] = None,
        governance_data: Optional[Dict] = None
    ) -> str:
        """
        Generate comprehensive ESG summary from all three pillars
        
        Args:
            emissions_data: Environmental metrics summary
            social_data: Social metrics summary
            governance_data: Governance metrics summary
            
        Returns:
            Comprehensive ESG summary
        """
        prompt = f"""
You are an ESG reporting expert. Create a comprehensive ESG summary report based on the following data:

Environmental Data:
{emissions_data if emissions_data else "Not provided"}

Social Data:
{social_data if social_data else "Not provided"}

Governance Data:
{governance_data if governance_data else "Not provided"}

Provide:
1. Executive Summary (2-3 sentences)
2. Key Highlights (3-5 bullet points)
3. Areas of Strength
4. Areas for Improvement
5. Strategic Recommendations

Keep the response professional and actionable, under 300 words.
"""
        
        return self.generate_text(prompt, temperature=0.5)
    
    def answer_esg_question(self, question: str, context: Dict[str, Any]) -> str:
        """
        Answer user questions about ESG data
        
        Args:
            question: User's question
            context: Relevant ESG data context
            
        Returns:
            AI-generated answer
        """
        prompt = f"""
You are an ESG expert assistant for Aurora Renewables. Answer the following question based on the provided context.

Context:
{context}

Question: {question}

Provide a clear, concise answer with specific data points when relevant. If the question cannot be answered with the given context, explain what information would be needed.
"""
        
        return self.generate_text(prompt, temperature=0.6)


# Example usage
if __name__ == "__main__":
    # Initialize client
    # Make sure to set GCP_PROJECT_ID environment variable or pass it directly
    client = GeminiClient(
        project_id="memory-477122",  # Replace with your project ID
        location="us-central1"
    )
    
    # Test basic generation
    print("\n" + "="*60)
    print("Testing basic text generation...")
    print("="*60)
    response = client.generate_text(
        "Explain the importance of ESG metrics in renewable energy companies in 2 sentences."
    )
    print(response)
    
    # Test chat
    print("\n" + "="*60)
    print("Testing chat session...")
    print("="*60)
    client.start_chat(context="You are an ESG analyst for Aurora Renewables.")
    response1 = client.send_message("What are the key environmental metrics we should track?")
    print(f"Q: What are the key environmental metrics we should track?")
    print(f"A: {response1}")
    
    # Test ESG data analysis
    print("\n" + "="*60)
    print("Testing ESG data analysis...")
    print("="*60)
    sample_data = [
        {"month": "Jan", "value": 250},
        {"month": "Feb", "value": 230},
        {"month": "Mar", "value": 210}
    ]
    analysis = client.analyze_esg_data(
        metric_name="Carbon Emissions (tons CO2)",
        data=sample_data,
        metric_type="emissions"
    )
    print(analysis)

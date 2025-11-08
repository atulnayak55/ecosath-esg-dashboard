"""
AI Chat Service - SQLite-based insights for ESG Dashboards
Retrieves pre-generated insights from SQLite databases
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import sqlite3
import re

app = FastAPI(title="ESG AI Chat Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database paths
DB_PATHS = {
    'emissions': 'emissions_ai_insights.db',
    'social': 'social_ai_insights.db',
    'governance': 'governance_ai_insights.db'
}

# Chat session storage (in production, use Redis or database)
chat_sessions = {}

class Message(BaseModel):
    type: str
    content: str
    time: str

class ChatRequest(BaseModel):
    message: str
    context: str  # emissions, social, governance, general
    page_data: Optional[Dict] = None
    conversation_history: Optional[List[Message]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

def build_system_context(context: str, page_data: Dict = None) -> str:
    """Build system context based on the page"""
    base_context = """You are an ESG (Environmental, Social, Governance) AI Assistant for Aurora Renewables, 
a renewable energy company. You help users understand their sustainability metrics, identify trends, 
and provide actionable insights. Be concise, helpful, and data-driven in your responses."""

    context_details = {
        "emissions": """
        You are analyzing EMISSIONS data from Aurora Renewables' monitoring system.
        Key metrics include:
        - CO2 emissions (tons)
        - Energy consumption (MWh)
        - Renewable energy percentage
        - Waste generated (tons)
        - Water usage (cubic meters)
        - Carbon offset credits
        - Tree planting initiatives
        
        Provide insights on environmental impact, trends, and sustainability improvements.
        """,
        "social": """
        You are analyzing SOCIAL IMPACT metrics from Aurora Renewables.
        Key metrics include:
        - Employee wellbeing (satisfaction scores, work-life balance, benefits)
        - Diversity & inclusion (gender diversity, minority representation, pay equity)
        - Community impact (investment, volunteer hours, beneficiaries)
        - Health & safety (incident rate, training hours, compliance)
        
        Provide insights on workforce culture, inclusivity, community engagement, and safety.
        """,
        "governance": """
        You are analyzing GOVERNANCE metrics from Aurora Renewables.
        Key metrics include:
        - Board composition (independence, diversity, expertise)
        - Compliance metrics (audit score, policy adherence, certifications)
        - ESG ratings (overall scores from rating agencies)
        - Transparency & disclosure (reporting scores, stakeholder engagement)
        
        Provide insights on corporate governance, compliance status, and accountability.
        """
    }
    
    system_prompt = base_context + "\n" + context_details.get(context, "")
    
    if page_data:
        system_prompt += "\n\n=== CURRENT DASHBOARD DATA ===\n"
        
        # Add dashboard name
        if 'dashboard' in page_data:
            system_prompt += f"Dashboard: {page_data['dashboard']}\n"
        
        # Add currently displayed metric
        if 'current_metric' in page_data:
            system_prompt += f"Currently viewing: {page_data['current_metric']}\n"
        
        # Add selected time period for emissions
        if 'selected_period' in page_data:
            system_prompt += f"Time period: {page_data['selected_period']}\n"
        
        # Add current metric statistics
        if 'current_metric_stats' in page_data:
            stats = page_data['current_metric_stats']
            system_prompt += f"\nCurrent Metric Details:\n"
            
            if 'metric_name' in stats:
                system_prompt += f"- Metric: {stats['metric_name']}\n"
            
            if 'metric_unit' in stats:
                system_prompt += f"- Unit: {stats['metric_unit']}\n"
            
            if 'latest_value' in stats:
                system_prompt += f"- Latest Value: {stats['latest_value']}\n"
            
            if 'average_value' in stats:
                system_prompt += f"- Average: {stats['average_value']}\n"
            
            if 'trend' in stats:
                system_prompt += f"- Trend: {stats['trend']}\n"
            
            if 'percent_change' in stats:
                system_prompt += f"- Change: {stats['percent_change']}%\n"
            
            if 'data_range' in stats:
                system_prompt += f"- Data Range: {stats['data_range']}\n"
            
            # Add sub-statistics for social/governance
            if 'statistics' in stats:
                system_prompt += "\nDetailed Statistics:\n"
                for key, value in stats['statistics'].items():
                    system_prompt += f"  {key}:\n"
                    for k, v in value.items():
                        system_prompt += f"    - {k}: {v}\n"
        
        # Add dashboard metric cards summary
        if 'dashboard_metrics' in page_data:
            system_prompt += "\nAll Dashboard Metrics:\n"
            for metric, value in page_data['dashboard_metrics'].items():
                system_prompt += f"- {metric}: {value}\n"
        
        # Add available metrics
        if 'metrics_available' in page_data:
            system_prompt += f"\nAvailable metrics: {', '.join(page_data['metrics_available'])}\n"
        
        system_prompt += "\n=== END DASHBOARD DATA ===\n"
    
    return system_prompt

def format_conversation_history(history: List[Message]) -> str:
    """Format conversation history for Gemini"""
    if not history:
        return ""
    
    formatted = "\n\nPrevious conversation:\n"
    for msg in history[-6:]:  # Last 6 messages for context
        role = "User" if msg.type == "user" else "Assistant"
        formatted += f"{role}: {msg.content}\n"
    
    return formatted

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests with Gemini AI"""
    try:
        print(f"\n📨 Received chat request:")
        print(f"   Message: {request.message}")
        print(f"   Context: {request.context}")
        print(f"   Has page data: {request.page_data is not None}")
        
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        # Build context
        system_context = build_system_context(request.context, request.page_data)
        conversation_history = format_conversation_history(request.conversation_history)
        
        # Combine into full prompt
        full_prompt = f"""{system_context}

{conversation_history}

User question: {request.message}

Please provide a helpful, concise response focused on the ESG metrics and data available. 
If the question is about specific numbers or trends, reference the data provided in the page context.
Keep your response under 150 words unless detailed analysis is specifically requested."""

        print(f"   Calling Gemini...")
        
        # Get response from Gemini
        ai_response = gemini_client.generate_text(
            prompt=full_prompt,
            temperature=0.7,
            max_output_tokens=500
        )
        
        print(f"   ✅ Got response: {ai_response[:100]}...")
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="Failed to generate AI response")
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/ai/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ESG AI Chat",
        "gemini_model": "gemini-2.5-flash",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ai/analyze")
async def analyze_metrics(data: Dict):
    """Analyze ESG metrics and provide insights"""
    try:
        metric_type = data.get("metric_type", "general")
        metric_data = data.get("data", {})
        
        analysis = gemini_client.analyze_esg_data(
            metric_name=data.get("metric_name", "ESG Metric"),
            data=metric_data,
            metric_type=metric_type
        )
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ESG AI Chat Service",
        "status": "running",
        "endpoints": {
            "chat": "/api/ai/chat",
            "analyze": "/api/ai/analyze",
            "health": "/api/ai/health"
        }
    }

if __name__ == "__main__":
    print("🤖 Starting ESG AI Chat Service...")
    print(f"📊 Project: {PROJECT_ID}")
    print(f"🚀 Server: http://127.0.0.1:8004")
    uvicorn.run(app, host="127.0.0.1", port=8004)

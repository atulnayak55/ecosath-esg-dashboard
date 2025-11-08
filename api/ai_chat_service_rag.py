"""
AI Chat Service - RAG with Text-to-SQL
Two-step process:
1. LLM generates SQL query from user question
2. Execute query and LLM analyzes the results
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import sqlite3
import json

# Import Gemini client
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient

app = FastAPI(title="ESG AI Chat Service - RAG")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "memory-477122")
gemini_client = GeminiClient(project_id=PROJECT_ID, location="us-central1")

# Database paths and schemas
DB_CONFIG = {
    'emissions': {
        'db_path': 'emissions_data.db',
        'tables': {
            'emissions': ['date', 'timestamp', 'travel_emissions', 'production_emissions', 'energy_consumption', 
                         'air_quality', 'energy_mix_renewable_pct', 'waste_generated', 'carbon_offset_credits', 'trees_planted'],
            'emissions_monthly': ['month', 'travel_emissions', 'production_emissions', 'energy_consumption',
                                 'air_quality', 'energy_mix_renewable_pct', 'waste_generated', 'carbon_offset_credits', 'trees_planted'],
            'emissions_summary': ['metric', 'unit', 'avg_value', 'latest_value']
        },
        'description': 'Emissions data with daily records for past year. Use emissions table for daily data, emissions_monthly for monthly trends, emissions_summary for quick stats. All emissions in kg CO2e, energy in kWh.'
    },
    'social': {
        'db_path': 'social_metrics.db',
        'tables': {
            'employee_wellbeing': ['period', 'satisfaction_score', 'work_life_balance', 'benefits_rating'],
            'diversity_inclusion': ['period', 'gender_diversity_pct', 'minority_representation_pct', 'pay_equity_index'],
            'community_impact': ['period', 'community_investment', 'volunteer_hours', 'beneficiaries_reached'],
            'health_safety': ['period', 'incident_rate', 'training_hours', 'compliance_score']
        },
        'description': 'Social impact metrics including employee wellbeing, diversity, community engagement, and safety'
    },
    'governance': {
        'db_path': 'governance_metrics.db',
        'tables': {
            'board_composition': ['quarter', 'independence_pct', 'diversity_pct', 'expertise_score'],
            'compliance_metrics': ['quarter', 'audit_score', 'policy_adherence_pct', 'certifications_count'],
            'esg_ratings': ['quarter', 'msci_score', 'sustainalytics_score', 'cdp_score'],
            'transparency_disclosure': ['quarter', 'reporting_score', 'stakeholder_engagement', 'data_verification_pct']
        },
        'description': 'Governance metrics including board composition, compliance, ESG ratings, and transparency'
    }
}

class Message(BaseModel):
    type: str
    content: str
    time: str

class ChatRequest(BaseModel):
    message: str
    context: str  # emissions, social, governance
    page_data: Optional[Dict] = None
    conversation_history: Optional[List[Message]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    query_results: Optional[List[Dict]] = None
    session_id: str
    timestamp: str

def get_database_schema(context: str) -> str:
    """Generate database schema description for the LLM"""
    config = DB_CONFIG.get(context, {})
    if not config:
        return "No database schema available"
    
    schema = f"Database: {config['description']}\n\nTables:\n"
    for table_name, columns in config['tables'].items():
        schema += f"\n**{table_name}** table:\n"
        schema += f"  Columns: {', '.join(columns)}\n"
        
        # Add sample data
        try:
            conn = sqlite3.connect(config['db_path'])
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
            rows = cursor.fetchall()
            if rows:
                schema += f"  Sample data (first 2 rows):\n"
                for row in rows:
                    schema += f"    {dict(zip(columns, row))}\n"
            conn.close()
        except Exception as e:
            schema += f"  (Could not fetch sample data: {e})\n"
    
    return schema

def generate_sql_query(user_question: str, context: str, page_data: Optional[Dict] = None) -> str:
    """Step 1: Use LLM to generate SQL query from user question"""
    
    config = DB_CONFIG.get(context, {})
    tables_list = list(config['tables'].keys())
    
    # Simplified schema - just column names
    schema_simple = ""
    for table, columns in config['tables'].items():
        schema_simple += f"{table}: {', '.join(columns)}\n"
    
    prompt = f"""Generate SQL for: "{user_question}"

Tables:
{schema_simple}

Rules:
- Return ONLY the SQL query
- Use ORDER BY date/month DESC
- Add LIMIT 10 for large results
- For trends: use emissions_monthly table
- For latest values: use emissions table ORDER BY date DESC LIMIT 1

SQL:"""

    try:
        sql_query = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.1,
            max_output_tokens=150  # Reduced from 300
        )
        
        # Clean up the SQL query
        sql_query = sql_query.strip()
        # Remove markdown code blocks if present
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        # Remove any trailing semicolons or extra whitespace
        sql_query = sql_query.rstrip(';').strip()
        
        print(f"📝 Generated SQL: {sql_query}")
        return sql_query
        
    except Exception as e:
        print(f"❌ Error generating SQL: {e}")
        raise Exception(f"Failed to generate SQL query: {e}")

def execute_sql_query(sql_query: str, context: str) -> List[Dict]:
    """Execute the generated SQL query and return results"""
    config = DB_CONFIG.get(context, {})
    if not config:
        raise Exception(f"No database configuration for context: {context}")
    
    try:
        conn = sqlite3.connect(config['db_path'])
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Security: Basic SQL injection prevention
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
            raise Exception("Query contains forbidden operations")
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = [dict(row) for row in rows]
        
        conn.close()
        
        print(f"✅ Query returned {len(results)} rows")
        return results
        
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        raise Exception(f"Failed to execute query: {e}")

def analyze_results_with_llm(user_question: str, sql_query: str, results: List[Dict], context: str) -> str:
    """Step 2: Use LLM to analyze query results and answer user question"""
    
    # Format results for LLM
    results_str = json.dumps(results, indent=2, default=str)
    
    # Limit results size if too large
    if len(results_str) > 5000:
        results_str = json.dumps(results[:20], indent=2, default=str) + f"\n... ({len(results)} total rows)"
    
    prompt = f"""You are an ESG (Environmental, Social, Governance) data analyst for Aurora Renewables, a renewable energy company.

Context: {context.upper()} Dashboard

User Question: "{user_question}"

SQL Query Executed:
```sql
{sql_query}
```

Query Results:
{results_str}

Based on the query results, provide a clear, insightful answer to the user's question. 

Guidelines:
1. Be specific and reference actual numbers from the data
2. Identify trends (increasing, decreasing, stable)
3. Provide context (is this good/bad compared to benchmarks?)
4. Give actionable insights or recommendations
5. Keep response concise (under 150 words) unless detailed analysis is requested
6. Use bullet points for clarity when appropriate
7. If data shows concerning trends, mention them with suggestions

Answer:"""

    try:
        analysis = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=600
        )
        
        print(f"✅ Generated analysis: {analysis[:100]}...")
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing results: {e}")
        raise Exception(f"Failed to analyze results: {e}")

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests with RAG Text-to-SQL pipeline"""
    try:
        print(f"\n📨 Received chat request:")
        print(f"   Message: {request.message}")
        print(f"   Context: {request.context}")
        
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        # Step 1: Generate SQL query
        print(f"   🔧 Step 1: Generating SQL query...")
        sql_query = generate_sql_query(request.message, request.context, request.page_data)
        
        # Step 2: Execute SQL query
        print(f"   🔧 Step 2: Executing SQL query...")
        query_results = execute_sql_query(sql_query, request.context)
        
        # Step 3: Analyze results with LLM
        print(f"   🔧 Step 3: Analyzing results...")
        analysis = analyze_results_with_llm(request.message, sql_query, query_results, request.context)
        
        print(f"   ✅ Response generated successfully")
        
        return ChatResponse(
            response=analysis,
            sql_query=sql_query,
            query_results=query_results[:10] if len(query_results) > 10 else query_results,  # Limit to 10 rows in response
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return helpful error message
        return ChatResponse(
            response=f"I apologize, but I encountered an error analyzing your question. {str(e)}. Please try rephrasing your question or ask about specific metrics.",
            sql_query=None,
            query_results=None,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/ai/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ESG AI Chat - RAG with Text-to-SQL",
        "gemini_model": "gemini-2.5-flash",
        "approach": "Two-step: SQL generation → Query execution → Result analysis",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ai/schema/{context}")
async def get_schema(context: str):
    """Get database schema for a specific context"""
    try:
        schema = get_database_schema(context)
        return {
            "context": context,
            "schema": schema,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ESG AI Chat Service - RAG",
        "status": "running",
        "approach": "Text-to-SQL with LLM analysis",
        "endpoints": {
            "chat": "/api/ai/chat",
            "health": "/api/ai/health",
            "schema": "/api/ai/schema/{context}"
        }
    }

if __name__ == "__main__":
    print("🤖 Starting ESG AI Chat Service (RAG with Text-to-SQL)...")
    print(f"📊 Project: {PROJECT_ID}")
    print(f"🚀 Server: http://127.0.0.1:8004")
    print(f"💡 Approach: User Question → SQL Generation → Query Execution → LLM Analysis")
    uvicorn.run(app, host="127.0.0.1", port=8004)

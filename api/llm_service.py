"""
LLM API Service for Text-to-SQL
FastAPI service that exposes the Text-to-SQL pipeline as REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path
from typing import Optional, Dict, List
import os

# Add llm directory to path
sys.path.append(str(Path(__file__).parent.parent / "llm"))
sys.path.append(str(Path(__file__).parent))

from db_client import DatabaseClient
from llm import SQLPromptGenerator
from gemini_client import GeminiClient

app = FastAPI(title="LLM Text-to-SQL API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    database: str = "emissions"  # emissions, social, or governance

class QuestionResponse(BaseModel):
    success: bool
    question: str
    sql_query: Optional[str] = None
    results: Optional[List[Dict]] = None
    analysis: Optional[str] = None
    error: Optional[str] = None
    row_count: int = 0

# Database paths mapping
DATABASE_PATHS = {
    "emissions": "emissions_data.db",
    "social": "social_metrics.db",
    "governance": "governance_metrics.db"
}

# Global orchestrator instances
orchestrators = {}

def get_orchestrator(db_name: str):
    """Get or create orchestrator for database"""
    if db_name not in orchestrators:
        db_path = Path(__file__).parent.parent / DATABASE_PATHS[db_name]
        
        # Initialize components
        db_client = DatabaseClient(str(db_path))
        prompt_generator = SQLPromptGenerator(str(db_path))
        gemini_client = GeminiClient(
            project_id=os.getenv("GCP_PROJECT_ID", "memory-477122"),
            location="us-central1"
        )
        
        orchestrators[db_name] = {
            "db_client": db_client,
            "prompt_generator": prompt_generator,
            "gemini_client": gemini_client,
            "db_path": str(db_path)
        }
    
    return orchestrators[db_name]

def generate_sql(prompt_generator, gemini_client, user_question: str) -> Optional[str]:
    """Generate SQL from question"""
    try:
        prompt = prompt_generator.generate_sql_prompt(user_question, include_samples=True)
        
        response = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.1,
            max_output_tokens=500
        )
        
        if not response:
            return None
        
        # Clean SQL
        sql_query = response.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Remove leading text before SELECT/WITH
        lines = sql_query.split('\n')
        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            if line_upper.startswith('SELECT') or line_upper.startswith('WITH'):
                sql_query = '\n'.join(lines[i:])
                break
        
        return sql_query.strip()
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None

def execute_query(db_client, sql_query: str) -> Optional[List[Dict]]:
    """Execute SQL query"""
    try:
        if not sql_query.strip().upper().startswith(("SELECT", "WITH")):
            return None
        
        conn = db_client.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def generate_analysis(prompt_generator, gemini_client, question: str, sql: str, results: List[Dict]) -> Optional[str]:
    """Generate analysis of results"""
    try:
        prompt = prompt_generator.generate_analysis_prompt(question, sql, results)
        
        response = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=500
        )
        
        return response
    except Exception as e:
        print(f"Error generating analysis: {e}")
        return None

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "LLM Text-to-SQL API"}

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Process a natural language question and return SQL + results + analysis
    """
    try:
        # Validate database
        if request.database not in DATABASE_PATHS:
            raise HTTPException(status_code=400, detail=f"Invalid database: {request.database}")
        
        # Get orchestrator
        orch = get_orchestrator(request.database)
        
        # Generate SQL
        sql_query = generate_sql(orch["prompt_generator"], orch["gemini_client"], request.question)
        
        if not sql_query:
            return QuestionResponse(
                success=False,
                question=request.question,
                error="Failed to generate SQL query"
            )
        
        # Execute query
        results = execute_query(orch["db_client"], sql_query)
        
        if results is None:
            return QuestionResponse(
                success=False,
                question=request.question,
                sql_query=sql_query,
                error="Failed to execute query"
            )
        
        # Generate analysis
        analysis = generate_analysis(
            orch["prompt_generator"], 
            orch["gemini_client"], 
            request.question, 
            sql_query, 
            results
        )
        
        return QuestionResponse(
            success=True,
            question=request.question,
            sql_query=sql_query,
            results=results[:50],  # Limit to 50 rows for response size
            analysis=analysis,
            row_count=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/databases")
async def list_databases():
    """List available databases"""
    return {
        "databases": list(DATABASE_PATHS.keys())
    }

@app.get("/examples/{database}")
async def get_examples(database: str):
    """Get example questions for a database"""
    try:
        if database not in DATABASE_PATHS:
            raise HTTPException(status_code=400, detail=f"Invalid database: {database}")
        
        orch = get_orchestrator(database)
        examples = orch["prompt_generator"].get_example_questions()
        
        return {
            "database": database,
            "examples": examples[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting LLM Text-to-SQL API on port 8005")
    print("📚 Available databases: emissions, social, governance")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)

"""
Main orchestrator for LLM-powered Text-to-SQL system
Manages the flow: User Question → SQL Generation → Query Execution → Analysis
"""
import sys
import os
import sqlite3
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from db_client import DatabaseClient
from llm import SQLPromptGenerator
sys.path.append(str(Path(__file__).parent.parent / "api"))
from gemini_client import GeminiClient


class TextToSQLOrchestrator:
    """Main orchestrator for Text-to-SQL pipeline"""
    
    def __init__(self, db_path: str, project_id: str = "memory-477122", location: str = "us-central1"):
        """
        Initialize orchestrator
        
        Args:
            db_path: Path to SQLite database
            project_id: GCP project ID for Gemini
            location: GCP location for Gemini
        """
        self.db_path = db_path
        self.db_client = DatabaseClient(db_path)
        self.prompt_generator = SQLPromptGenerator(db_path)
        self.gemini_client = GeminiClient(project_id=project_id, location=location)
        
        print(f"✅ Initialized Text-to-SQL for database: {self.db_client.db_name}")
    
    def process_question(self, user_question: str) -> Dict:
        """
        Process user question through complete pipeline
        
        Args:
            user_question: User's natural language question
            
        Returns:
            Dictionary with results and metadata
        """
        result = {
            "question": user_question,
            "success": False,
            "error": None,
            "sql_query": None,
            "results": None,
            "analysis": None,
            "metadata": {}
        }
        
        try:
            # Step 1: Log the question
            print(f"\n🔍 Question: {user_question}")
            
            # Step 2: Generate SQL query using LLM
            print(f"\n🤖 Generating SQL query...")
            sql_query = self._generate_sql(user_question)
            
            if not sql_query:
                result["error"] = "Failed to generate SQL query"
                return result
            
            result["sql_query"] = sql_query
            print(f"✅ Generated SQL:\n{sql_query}")
            
            # Step 3: Execute SQL query
            print(f"\n⚡ Executing query...")
            query_results = self._execute_query(sql_query)
            
            if query_results is None:
                result["error"] = "Failed to execute query"
                return result
            
            result["results"] = query_results
            result["metadata"]["row_count"] = len(query_results)
            print(f"✅ Query returned {len(query_results)} rows")
            
            # Step 4: Generate analysis using LLM
            print(f"\n📊 Generating analysis...")
            analysis = self._generate_analysis(user_question, sql_query, query_results)
            
            if analysis:
                result["analysis"] = analysis
                print(f"✅ Analysis generated")
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error: {e}")
        
        return result
    
    def _generate_sql(self, user_question: str) -> Optional[str]:
        """
        Generate SQL query from user question
        
        Args:
            user_question: User's question
            
        Returns:
            SQL query string or None
        """
        try:
            # Generate prompt
            prompt = self.prompt_generator.generate_sql_prompt(user_question, include_samples=True)
            
            # Call Gemini
            response = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.1,  # Low temperature for precise SQL
                max_output_tokens=500
            )
            
            if not response:
                return None
            
            # Clean up response - remove markdown code blocks if present
            sql_query = response.strip()
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            # Remove any leading text before SELECT/WITH
            lines = sql_query.split('\n')
            for i, line in enumerate(lines):
                line_upper = line.strip().upper()
                if line_upper.startswith('SELECT') or line_upper.startswith('WITH'):
                    sql_query = '\n'.join(lines[i:])
                    break
            
            sql_query = sql_query.strip()
            
            # Basic validation - should start with SELECT or WITH
            if not any(sql_query.upper().startswith(cmd) for cmd in ["SELECT", "WITH"]):
                print(f"⚠️  Warning: Query doesn't start with SELECT or WITH")
                print(f"Raw response: {response[:200]}")
                return None
            
            return sql_query
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            return None
    
    def _execute_query(self, sql_query: str) -> Optional[List[Dict]]:
        """
        Execute SQL query safely
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            List of result dictionaries or None
        """
        try:
            # Only allow SELECT queries for safety
            if not sql_query.strip().upper().startswith(("SELECT", "WITH")):
                print(f"❌ Only SELECT queries are allowed")
                return None
            
            conn = self.db_client.get_connection()
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(sql_query)
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            
            conn.close()
            
            return results
            
        except sqlite3.Error as e:
            print(f"❌ SQL Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def _generate_analysis(self, user_question: str, sql_query: str, results: List[Dict]) -> Optional[str]:
        """
        Generate natural language analysis of results
        
        Args:
            user_question: Original question
            sql_query: SQL query executed
            results: Query results
            
        Returns:
            Analysis text or None
        """
        try:
            # Generate analysis prompt
            prompt = self.prompt_generator.generate_analysis_prompt(
                user_question, 
                sql_query, 
                results
            )
            
            # Call Gemini
            response = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.7,  # Higher temperature for natural analysis
                max_output_tokens=500
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating analysis: {e}")
            return None
    
    def get_example_questions(self) -> List[str]:
        """Get example questions for this database"""
        return self.prompt_generator.get_example_questions()
    
    def print_result(self, result: Dict):
        """Pretty print the result"""
        print("\n" + "="*80)
        print("RESULT")
        print("="*80)
        
        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"\n📝 Question: {result['question']}")
        print(f"\n🔍 SQL Query:\n{result['sql_query']}")
        print(f"\n📊 Results ({result['metadata']['row_count']} rows):")
        
        if result['results']:
            # Show first 10 rows
            for i, row in enumerate(result['results'][:10], 1):
                print(f"  {i}. {row}")
            
            if len(result['results']) > 10:
                print(f"  ... and {len(result['results']) - 10} more rows")
        
        if result['analysis']:
            print(f"\n💡 Analysis:\n{result['analysis']}")
        
        print("\n" + "="*80)


def main():
    """Main entry point for testing"""
    import os
    
    # Set GCP project ID
    os.environ['GCP_PROJECT_ID'] = 'memory-477122'
    
    # Initialize orchestrator with emissions database
    print("🚀 Initializing Text-to-SQL Orchestrator")
    print("="*80)
    
    # Use absolute path to database
    db_path = Path(__file__).parent.parent / "emissions_data.db"
    orchestrator = TextToSQLOrchestrator(str(db_path))
    
    # Show example questions
    print("\n📚 Example Questions:")
    examples = orchestrator.get_example_questions()
    for i, q in enumerate(examples[:5], 1):
        print(f"  {i}. {q}")
    
    # Test with a sample question
    print("\n" + "="*80)
    print("TESTING WITH SAMPLE QUESTION")
    print("="*80)
    
    test_question = "What is the average AQI for the last 30 days?"
    result = orchestrator.process_question(test_question)
    orchestrator.print_result(result)
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE (type 'quit' to exit)")
    print("="*80)
    
    while True:
        try:
            question = input("\n💬 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            result = orchestrator.process_question(question)
            orchestrator.print_result(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

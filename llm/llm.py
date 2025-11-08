"""
LLM Prompt Generator for Text-to-SQL
Generates prompts with database context for SQL query generation
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from db_client import DatabaseClient


class SQLPromptGenerator:
    """Generate prompts for LLM to create SQL queries"""
    
    def __init__(self, db_path: str):
        """
        Initialize prompt generator with database
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_client = DatabaseClient(db_path)
        self.db_name = self.db_client.db_name
    
    def generate_sql_prompt(self, user_question: str, include_samples: bool = True) -> str:
        """
        Generate complete prompt for SQL generation
        
        Args:
            user_question: User's natural language question
            include_samples: Whether to include sample data in context
            
        Returns:
            Complete prompt string for LLM
        """
        # Get database context
        db_context = self.db_client.get_llm_context(include_samples=include_samples)
        
        # Build the prompt
        prompt = f"""You are an expert SQL query generator. Your task is to convert natural language questions into valid SQLite queries.

DATABASE SCHEMA:
{db_context}

IMPORTANT RULES:
1. Generate ONLY valid SQLite syntax
2. Use proper table and column names from the schema above
3. Return ONLY the SQL query, no explanations or markdown
4. Use appropriate WHERE, GROUP BY, ORDER BY, and LIMIT clauses as needed
5. For date queries, use SQLite date functions (date(), strftime(), etc.)
6. For aggregations, use proper GROUP BY clauses
7. Always use column names exactly as shown in the schema
8. When asked "which day/date" questions, SELECT the date column AND the value column
9. When asked "highest/lowest/maximum/minimum", include ORDER BY and LIMIT 1
10. For "average" questions, return the numeric value directly

EXAMPLES:
Question: "Which day had the highest AQI?"
SQL: SELECT date, aqi FROM air_quality ORDER BY aqi DESC LIMIT 1

Question: "What is the average production emissions?"
SQL: SELECT AVG(production_tco2e) as avg_emissions FROM production_emissions

Question: "Show me energy consumption for last month"
SQL: SELECT date, electricity_kwh FROM energy_consumption WHERE date >= date('now', '-1 month') ORDER BY date

Question: "Energy consumption trend by month over the year"
SQL: SELECT strftime('%Y-%m', date) as month, SUM(electricity_kwh) as total_electricity FROM energy_consumption GROUP BY month ORDER BY month

Question: "Production emissions by month"
SQL: SELECT strftime('%Y-%m', date) as month, SUM(production_tco2e) as total_emissions FROM production_emissions GROUP BY month ORDER BY month

USER QUESTION:
{user_question}

SQL QUERY:"""

        return prompt
    
    def generate_analysis_prompt(self, user_question: str, sql_query: str, query_results: List[Dict]) -> str:
        """
        Generate prompt for analyzing SQL query results
        
        Args:
            user_question: Original user question
            sql_query: SQL query that was executed
            query_results: Results from the SQL query
            
        Returns:
            Prompt for LLM to analyze results
        """
        # Format results for display
        if not query_results:
            results_text = "No results found."
        elif len(query_results) == 1:
            # Single result - show as key-value pairs
            results_text = "Result:\n"
            for key, value in query_results[0].items():
                if isinstance(value, float):
                    results_text += f"  {key}: {value:.2f}\n"
                else:
                    results_text += f"  {key}: {value}\n"
        elif len(query_results) <= 15:
            # Show all results in table format
            results_text = f"All {len(query_results)} results:\n\n"
            results_text += self._format_results(query_results)
        else:
            # Show first 15 and summary
            results_text = f"First 15 of {len(query_results)} results:\n\n"
            results_text += self._format_results(query_results[:15])
            results_text += f"\n... and {len(query_results) - 15} more rows"
        
        prompt = f"""You are an expert data analyst for an ESG (Environmental, Social, Governance) dashboard.

USER QUESTION:
{user_question}

QUERY RESULTS:
{results_text}

TASK:
Analyze the data and provide a clear, insightful answer to the user's question.

FORMATTING RULES:
1. Start with the main insight immediately (no greetings)
2. For trends/patterns over multiple rows:
   - Describe the overall trend (increasing, decreasing, stable, fluctuating)
   - Mention highest and lowest values with their dates/periods
   - Note any significant changes or anomalies
3. Use specific numbers from the results
4. Format dates as human-readable (e.g., "November 2024" not "2024-11")
5. Use 1-2 emojis maximum for visual appeal
6. Keep response conversational but data-focused
7. If showing multiple data points, summarize the key pattern
8. Maximum 4-5 sentences

EXAMPLE GOOD RESPONSES:
- "Energy consumption shows an upward trend from November 2024 to November 2025. The lowest usage was 282,971 kWh in November 2024, while the highest reached 1,228,847 kWh in December 2024. Overall, monthly consumption averages around 983,671 kWh. 📈"

- "The highest AQI of 76 occurred on March 30, 2025, indicating moderate air quality."

RESPONSE:"""

        return prompt
    
    def _format_results(self, results: List[Dict]) -> str:
        """Format query results as a readable table"""
        if not results:
            return "No data"
        
        # Get column headers
        headers = list(results[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = max(
                len(str(header)),
                max(len(str(row[header])) for row in results)
            )
        
        # Format as table
        output = ""
        
        # Header row
        header_row = " | ".join(str(h).ljust(col_widths[h]) for h in headers)
        output += header_row + "\n"
        output += "-" * len(header_row) + "\n"
        
        # Data rows
        for row in results:
            values = []
            for header in headers:
                value = row[header]
                # Format numbers nicely
                if isinstance(value, float):
                    formatted = f"{value:.2f}".ljust(col_widths[header])
                else:
                    formatted = str(value).ljust(col_widths[header])
                values.append(formatted)
            output += " | ".join(values) + "\n"
        
        return output
    
    def get_example_questions(self) -> List[str]:
        """Get example questions based on database schema"""
        return self.db_client.get_example_questions()


if __name__ == "__main__":
    # Test with emissions database
    print("🧪 Testing SQL Prompt Generator\n")
    print("="*80)
    
    # Use absolute path to database
    db_path = Path(__file__).parent.parent / "emissions_data.db"
    generator = SQLPromptGenerator(str(db_path))
    
    # Test questions
    test_questions = [
        "What is the average AQI for the last 30 days?",
        "Show me the total production emissions for each month",
        "What are the top 5 days with highest energy consumption?",
        "How many flights were there in total?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {question}")
        print('='*80)
        
        # Generate prompt (without samples for shorter output)
        prompt = generator.generate_sql_prompt(question, include_samples=False)
        print(f"\nPrompt Preview (first 500 chars):")
        print(prompt[:500] + "...\n")
    
    # Show example questions
    print("\n" + "="*80)
    print("EXAMPLE QUESTIONS FROM DATABASE:")
    print("="*80)
    examples = generator.get_example_questions()
    for i, q in enumerate(examples[:10], 1):
        print(f"{i}. {q}")

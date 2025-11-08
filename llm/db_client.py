"""
Database Client for LLM Integration
Fetches database metadata, schema, and sample data for LLM context
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

class DatabaseClient:
    """Client to fetch database information for LLM context"""
    
    def __init__(self, db_path: str):
        """
        Initialize database client
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.db_name = Path(db_path).stem
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_table_names(self) -> List[str]:
        """
        Get all table names in the database
        
        Returns:
            List of table names
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """
        Get schema for a specific table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': bool(row[3]),
                'default_value': row[4],
                'primary_key': bool(row[5])
            })
        
        conn.close()
        return columns
    
    def get_column_names(self, table_name: str) -> List[str]:
        """
        Get column names for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column names
        """
        schema = self.get_table_schema(table_name)
        return [col['name'] for col in schema]
    
    def get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """
        Get sample rows from a table
        
        Args:
            table_name: Name of the table
            limit: Number of sample rows to fetch
            
        Returns:
            List of sample row dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        samples = [dict(row) for row in rows]
        
        conn.close()
        return samples
    
    def get_row_count(self, table_name: str) -> int:
        """
        Get total row count for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_column_stats(self, table_name: str, column_name: str) -> Dict:
        """
        Get statistics for a numeric column
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            
        Returns:
            Dictionary with min, max, avg, count statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                SELECT 
                    MIN({column_name}) as min_val,
                    MAX({column_name}) as max_val,
                    AVG({column_name}) as avg_val,
                    COUNT({column_name}) as count_val
                FROM {table_name}
            """)
            
            row = cursor.fetchone()
            stats = {
                'min': row[0],
                'max': row[1],
                'avg': row[2],
                'count': row[3]
            }
        except sqlite3.OperationalError:
            # Column might not be numeric
            stats = None
        
        conn.close()
        return stats
    
    def get_distinct_values(self, table_name: str, column_name: str, limit: int = 10) -> List:
        """
        Get distinct values for a column
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            limit: Maximum number of distinct values to return
            
        Returns:
            List of distinct values
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT DISTINCT {column_name} 
            FROM {table_name} 
            LIMIT {limit}
        """)
        
        values = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return values
    
    def get_date_range(self, table_name: str, date_column: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get date range for a date column
        
        Args:
            table_name: Name of the table
            date_column: Name of the date column
            
        Returns:
            Tuple of (min_date, max_date)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                SELECT 
                    MIN({date_column}) as min_date,
                    MAX({date_column}) as max_date
                FROM {table_name}
            """)
            
            row = cursor.fetchone()
            date_range = (row[0], row[1])
        except sqlite3.OperationalError:
            date_range = (None, None)
        
        conn.close()
        return date_range
    
    def get_full_metadata(self) -> Dict:
        """
        Get comprehensive metadata for the entire database
        
        Returns:
            Dictionary containing all database metadata
        """
        metadata = {
            'database_name': self.db_name,
            'database_path': self.db_path,
            'tables': {}
        }
        
        tables = self.get_table_names()
        
        for table in tables:
            schema = self.get_table_schema(table)
            row_count = self.get_row_count(table)
            samples = self.get_sample_data(table, limit=2)
            
            table_meta = {
                'row_count': row_count,
                'columns': [],
                'sample_data': samples
            }
            
            # Get detailed column information
            for col in schema:
                col_info = {
                    'name': col['name'],
                    'type': col['type'],
                    'primary_key': col['primary_key'],
                    'nullable': not col['notnull']
                }
                
                # Try to get stats for numeric columns
                if col['type'].upper() in ['INTEGER', 'REAL', 'NUMERIC', 'FLOAT']:
                    stats = self.get_column_stats(table, col['name'])
                    if stats:
                        col_info['statistics'] = stats
                
                # Try to detect date columns and get date range
                if 'date' in col['name'].lower() or 'time' in col['name'].lower() or col['name'] in ['month', 'quarter', 'period']:
                    date_range = self.get_date_range(table, col['name'])
                    if date_range[0] and date_range[1]:
                        col_info['date_range'] = {
                            'min': date_range[0],
                            'max': date_range[1]
                        }
                
                table_meta['columns'].append(col_info)
            
            metadata['tables'][table] = table_meta
        
        return metadata
    
    def get_llm_context(self, include_samples: bool = True) -> str:
        """
        Generate formatted context string for LLM
        
        Args:
            include_samples: Whether to include sample data
            
        Returns:
            Formatted string with database information
        """
        metadata = self.get_full_metadata()
        
        context = f"DATABASE: {metadata['database_name']}\n"
        context += f"Total Tables: {len(metadata['tables'])}\n\n"
        
        for table_name, table_info in metadata['tables'].items():
            context += f"TABLE: {table_name}\n"
            context += f"  Rows: {table_info['row_count']}\n"
            context += f"  Columns:\n"
            
            for col in table_info['columns']:
                context += f"    - {col['name']} ({col['type']})"
                
                if col.get('primary_key'):
                    context += " [PRIMARY KEY]"
                
                if col.get('statistics'):
                    stats = col['statistics']
                    context += f" [MIN: {stats['min']:.2f}, MAX: {stats['max']:.2f}, AVG: {stats['avg']:.2f}]"
                
                if col.get('date_range'):
                    dr = col['date_range']
                    context += f" [RANGE: {dr['min']} to {dr['max']}]"
                
                context += "\n"
            
            if include_samples and table_info['sample_data']:
                context += f"  Sample Data (first 2 rows):\n"
                for i, row in enumerate(table_info['sample_data'], 1):
                    context += f"    Row {i}: {json.dumps(row, default=str)}\n"
            
            context += "\n"
        
        return context
    
    def get_example_questions(self) -> List[str]:
        """
        Generate example questions based on database schema
        
        Returns:
            List of example questions
        """
        metadata = self.get_full_metadata()
        questions = []
        
        for table_name, table_info in metadata['tables'].items():
            # Generic questions
            questions.append(f"Show me all data from {table_name}")
            questions.append(f"What is the total count in {table_name}?")
            
            # Questions based on columns
            for col in table_info['columns']:
                col_name = col['name']
                
                # Numeric columns
                if col.get('statistics'):
                    questions.append(f"What is the average {col_name} in {table_name}?")
                    questions.append(f"Show me the maximum {col_name} in {table_name}")
                
                # Date columns
                if col.get('date_range'):
                    questions.append(f"Show me {table_name} data sorted by {col_name}")
                    questions.append(f"What is the latest {col_name} in {table_name}?")
        
        return questions[:20]  # Return first 20 examples


if __name__ == "__main__":
    # Test with emissions database
    print("🔍 Testing Database Client with emissions_data.db\n")
    
    db_client = DatabaseClient("emissions_data.db")
    
    # Test basic methods
    print("Tables:", db_client.get_table_names())
    print("\n" + "="*80 + "\n")
    
    # Get full metadata
    metadata = db_client.get_full_metadata()
    print(json.dumps(metadata, indent=2, default=str))
    
    print("\n" + "="*80 + "\n")
    
    # Get LLM context
    llm_context = db_client.get_llm_context()
    print("LLM CONTEXT:\n")
    print(llm_context)
    
    print("\n" + "="*80 + "\n")
    
    # Get example questions
    questions = db_client.get_example_questions()
    print("EXAMPLE QUESTIONS:\n")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")

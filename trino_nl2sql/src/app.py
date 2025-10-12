#!/usr/bin/env python3
"""
Trino NL2SQL Flask Application
Natural Language to SQL query interface for Trino
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Add src directory to Python path
src_dir = Path(__file__).parent.resolve()
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
project_root = src_dir.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Import modules
from sql_generator import SQLGenerator
from trino_executor import TrinoExecutor
from result_formatter import ResultFormatter

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=str(src_dir / 'templates'),
    static_folder=str(src_dir / 'static')
)

# Initialize components
sql_generator = SQLGenerator()
trino_executor = TrinoExecutor()
result_formatter = ResultFormatter()


@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    """Handle natural language query"""
    try:
        data = request.json
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided', 'status': 'error'}), 400

        logger.info(f"Processing question: {question}")

        # Step 1: Generate SQL
        try:
            sql_query = sql_generator.generate_sql(question)
            logger.info(f"Generated SQL: {sql_query}")
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return jsonify({
                'error': f'Failed to generate SQL query: {str(e)}',
                'status': 'error'
            }), 500

        # Step 2: Execute query
        try:
            results, columns = trino_executor.execute_query(sql_query)
            logger.info(f"Query executed, returned {len(results)} rows")
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return jsonify({
                'error': f'Failed to execute query: {str(e)}',
                'sql': sql_query,
                'status': 'error'
            }), 500

        # Step 3: Format results
        try:
            # Generate plain English explanation
            explanation = result_formatter.explain_results(question, sql_query, results)

            # Format as HTML table
            table_html = trino_executor.format_results_as_html(results, columns)

            return jsonify({
                'status': 'success',
                'question': question,
                'sql': sql_query,
                'explanation': explanation,
                'table': table_html,
                'row_count': len(results)
            })

        except Exception as e:
            logger.error(f"Result formatting failed: {e}")
            # Return results without explanation
            table_html = trino_executor.format_results_as_html(results, columns)
            return jsonify({
                'status': 'success',
                'question': question,
                'sql': sql_query,
                'explanation': f'Query returned {len(results)} rows.',
                'table': table_html,
                'row_count': len(results)
            })

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/schema', methods=['GET'])
def get_schema():
    """Get the database schema information"""
    try:
        schema_context = sql_generator.schema_loader.get_schema_context()
        return jsonify({
            'status': 'success',
            'schema': schema_context
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    logger.info(f"Starting Trino NL2SQL application")
    logger.info(f"Loading .env from: {env_path}")

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)

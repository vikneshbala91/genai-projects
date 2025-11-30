#!/usr/bin/env python3
"""
Trino NL2SQL Flask Application
Natural Language to SQL query interface for Trino
"""
import os
import sys
import logging
import atexit
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

# Load environment variables (trino_nl2sql/.env)
project_root = src_dir.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Import modules
from sql_generator import SQLGenerator
from result_formatter import ResultFormatter
from agents import SQLExecutorAgent
from conversation_store import ConversationStore

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=str(src_dir / 'templates'),
    static_folder=str(src_dir / 'static')
)

# Initialize components
sql_generator = SQLGenerator()
sql_executor = SQLExecutorAgent()
result_formatter = ResultFormatter()
conversation_store = ConversationStore()

# Ensure executor closes on shutdown
atexit.register(sql_executor.close)


@app.route('/conversations', methods=['POST'])
def create_conversation():
    """Create a new chat conversation and return its ID."""
    try:
        data = request.get_json(silent=True) or {}
        topic = data.get('topic')
        conversation_id = conversation_store.create_conversation(topic=topic)
        return jsonify({
            'status': 'success',
            'conversation_id': conversation_id,
            'storage': conversation_store.storage_backend
        })
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}", exc_info=True)
        return jsonify({
            'error': f'Unable to create conversation: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    """Handle natural language query"""
    conversation_id = None
    try:
        data = request.get_json(silent=True) or {}
        question = data.get('question', '').strip()
        conversation_id = data.get('conversation_id')

        if not question:
            return jsonify({
                'error': 'No question provided',
                'status': 'error',
                'conversation_id': conversation_id
            }), 400

        if not conversation_id:
            conversation_id = conversation_store.create_conversation(topic="Natural language SQL chat")

        conversation_store.append_message(
            conversation_id,
            role="user",
            content=question,
        )

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

        # Step 2: Execute query (single or multi-query plan)
        if isinstance(sql_query, list):
            multi_results = []
            for task in sql_query:
                step_id = task.get("id", "q?")
                objective = task.get("objective", "")
                step_sql = task.get("sql", "")
                try:
                    results, columns = sql_executor.execute(step_sql)
                    logger.info(f"[{step_id}] executed, returned {len(results)} rows")
                except Exception as e:
                    logger.error(f"[{step_id}] execution failed: {e}")
                    conversation_store.append_message(
                        conversation_id,
                        role="assistant",
                        content=f"Execution failed for step {step_id}",
                        metadata={"error": str(e), "sql": step_sql, "step": step_id, "plan_type": "multi_query"},
                    )
                    return jsonify({
                        'error': f'Failed to execute step {step_id}: {str(e)}',
                        'sql': step_sql,
                        'step': step_id,
                        'status': 'error',
                        'conversation_id': conversation_id
                    }), 500

                try:
                    explanation = result_formatter.explain_results(f"{question} ({objective})", step_sql, results)
                    table_html = sql_executor.format_results_as_html(results, columns)
                except Exception as e:
                    logger.error(f"[{step_id}] formatting failed: {e}")
                    table_html = sql_executor.format_results_as_html(results, columns)
                    explanation = f'Step {step_id} returned {len(results)} rows.'

                multi_results.append({
                    'step': step_id,
                    'objective': objective,
                    'sql': step_sql,
                    'explanation': explanation,
                    'table': table_html,
                    'row_count': len(results)
                })

            conversation_store.append_message(
                conversation_id,
                role="assistant",
                content=f"Executed {len(multi_results)}-step plan for: {question}",
                metadata={
                    "plan_type": "multi_query",
                    "steps": [
                        {
                            "id": step["step"],
                            "objective": step["objective"],
                            "sql": step["sql"],
                            "row_count": step["row_count"],
                        }
                        for step in multi_results
                    ],
                },
            )

            return jsonify({
                'status': 'success',
                'question': question,
                'plan_type': 'multi_query',
                'steps': multi_results,
                'conversation_id': conversation_id
            })

        else:
            try:
                results, columns = sql_executor.execute(sql_query)
                logger.info(f"Query executed, returned {len(results)} rows")
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                conversation_store.append_message(
                    conversation_id,
                    role="assistant",
                    content="Query execution failed",
                    metadata={"error": str(e), "sql": sql_query},
                )
                return jsonify({
                    'error': f'Failed to execute query: {str(e)}',
                    'sql': sql_query,
                    'status': 'error',
                    'conversation_id': conversation_id
                }), 500

            # Step 3: Format results
            try:
                # Generate plain English explanation
                explanation = result_formatter.explain_results(question, sql_query, results)

                # Format as HTML table
                table_html = sql_executor.format_results_as_html(results, columns)

                conversation_store.append_message(
                    conversation_id,
                    role="assistant",
                    content=explanation,
                    metadata={
                        "plan_type": "single",
                        "sql": sql_query,
                        "row_count": len(results),
                    },
                )

                return jsonify({
                    'status': 'success',
                    'question': question,
                    'sql': sql_query,
                    'explanation': explanation,
                    'table': table_html,
                    'row_count': len(results),
                    'conversation_id': conversation_id
                })

            except Exception as e:
                logger.error(f"Result formatting failed: {e}")
                # Return results without explanation
                table_html = sql_executor.format_results_as_html(results, columns)
                conversation_store.append_message(
                    conversation_id,
                    role="assistant",
                    content=f"Query returned {len(results)} rows.",
                    metadata={
                        "plan_type": "single",
                        "sql": sql_query,
                        "row_count": len(results),
                        "formatting_error": str(e),
                    },
                )
                return jsonify({
                    'status': 'success',
                    'question': question,
                    'sql': sql_query,
                    'explanation': f'Query returned {len(results)} rows.',
                    'table': table_html,
                    'row_count': len(results),
                    'conversation_id': conversation_id
                })

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        if conversation_id:
            conversation_store.append_message(
                conversation_id,
                role="assistant",
                content="Unexpected error while handling your request.",
                metadata={"error": str(e)},
            )
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'status': 'error',
            'conversation_id': conversation_id
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

    port = int(os.environ.get("PORT", 8080))
    if port != 8080:
        logger.info(f"Using custom port from PORT env: {port}")

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)

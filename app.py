"""
NL-to-SQL Pipeline - Flask Web Application

A modular pipeline for converting natural language to SQL using
open-source LLMs via HuggingFace Inference API.
"""

from flask import Flask, render_template, request, jsonify
import traceback

from pipeline.schema_processor import format_schema_for_prompt
from pipeline.reasoning import plan_query
from pipeline.sql_generator import generate_sql, format_sql
from pipeline.verifier import verify_and_correct
from pipeline.answer_generator import generate_answer

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate SQL from natural language question.
    
    Expects JSON body with:
    - schema: Database schema (CREATE TABLE statements)
    - question: Natural language question
    
    Returns JSON with:
    - success: Boolean
    - sql: Generated SQL query
    - reasoning: Chain-of-thought explanation
    - verification: Verification status and any corrections
    - error: Error message if failed
    """
    try:
        data = request.get_json()
        
        schema = data.get('schema', '').strip()
        question = data.get('question', '').strip()
        
        if not schema:
            return jsonify({
                'success': False,
                'error': 'Please provide a database schema'
            }), 400
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please provide a question'
            }), 400
        
        # Step 1: Process and format the schema
        formatted_schema = format_schema_for_prompt(schema)
        
        # Step 2: Generate chain-of-thought reasoning
        reasoning = plan_query(question, formatted_schema)
        
        # Step 3: Generate SQL based on reasoning
        sql = generate_sql(question, formatted_schema, reasoning)
        
        # Step 4: Verify and correct SQL
        verification = verify_and_correct(sql, question, schema)
        
        # Format the final SQL
        final_sql = format_sql(verification.sql)
        
        # Step 5: Generate human-readable answer
        answer = generate_answer(question, final_sql, reasoning)
        
        return jsonify({
            'success': True,
            'sql': final_sql,
            'reasoning': reasoning,
            'answer': answer,
            'verification': {
                'is_valid': verification.is_valid,
                'corrections_made': verification.corrections_made,
                'notes': verification.errors
            }
        })
        
    except ValueError as e:
        # Expected errors (API issues, etc.)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        # Unexpected errors
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("NL-to-SQL Pipeline")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("\nMake sure you have:")
    print("1. Added your HuggingFace API token to .env file")
    print("2. Installed requirements: pip install -r requirements.txt")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, port=5000)

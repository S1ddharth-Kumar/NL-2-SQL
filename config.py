# NL-to-SQL Pipeline Configuration

import os
from dotenv import load_dotenv


load_dotenv()

# HuggingFace Configuration

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

# Model Configuration

MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"



# Generation Parameters
MAX_NEW_TOKENS = 2048  # Increased for thorough reasoning on complex queries
TEMPERATURE = 0.1  # Low temperature for more deterministic SQL generation
# Verification Settings
MAX_CORRECTION_ATTEMPTS = 3

# System Prompts
SCHEMA_ANALYSIS_PROMPT = """You are a database expert. Analyze the following database schema and identify:
1. All tables and their columns with data types
2. Primary keys and foreign keys
3. Relationships between tables

Schema:
{schema}

Provide a clear, structured analysis."""

REASONING_PROMPT = """You are a SQL expert. Given a database schema and a natural language question, break down the query into logical steps.

Database Schema:
{schema}

Question: {question}

Think step by step and provide COMPLETE reasoning for each point:
1. What tables are needed and why?
2. What columns should be selected?
3. What joins are required (specify the join conditions)?
4. What filters/conditions apply?
5. Are there any aggregations, groupings, or ordering needed?
6. Any special considerations (NULL handling, duplicates, etc.)?

IMPORTANT: Provide your COMPLETE reasoning in a numbered list. Do not stop mid-sentence. Finish all your thoughts."""

SQL_GENERATION_PROMPT = """You are an expert SQL developer. Generate a SQL query based on the reasoning provided.

Database Schema:
{schema}

Question: {question}

Reasoning:
{reasoning}

Generate ONLY the SQL query without any explanation. The query should be syntactically correct and efficient."""

SQL_CORRECTION_PROMPT = """The following SQL query has an error. Please fix it.

Schema:
{schema}

Original Question: {question}

Faulty SQL:
{sql}

Error: {error}

Provide ONLY the corrected SQL query."""

ANSWER_GENERATION_PROMPT = """Based on the user's question and the generated SQL query, provide a clear, human-readable explanation of what this query does.

User's Question: {question}

Generated SQL:
{sql}

Reasoning Used:
{reasoning}

Write a concise 2-3 sentence explanation that:
1. Summarizes what data the query retrieves
2. Explains the key operations (joins, filters, aggregations) in plain English
3. Describes what the user will see in the results

Be direct and clear. Do not include any code or technical jargon."""

# SQL Forge - NL-to-SQL Pipeline

A modular pipeline that converts natural language questions into SQL queries using open-source AI models.

![Pipeline Overview](https://img.shields.io/badge/Model-Qwen2.5--Coder-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.8+-yellow)

---

## How It Works

The pipeline processes your request through **4 stages**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SCHEMA    │ -> │  REASONING  │ -> │     SQL     │ -> │  VERIFY &   │
│  PROCESSOR  │    │   (CoT)     │    │  GENERATOR  │    │   CORRECT   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

### Stage 1: Schema Processing

**File:** `pipeline/schema_processor.py`

The schema processor parses your CREATE TABLE statements and extracts:
- Table names and column definitions
- Data types and constraints
- Primary keys and foreign key relationships

**Input:**
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    total DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

**Output (formatted for LLM):**
```
DATABASE SCHEMA:
==================================================
Table: orders
------------------------------
Columns:
  - id: INT [PK]
  - customer_id: INT
  - total: DECIMAL(10,2)
Foreign Keys:
  - customer_id -> customers.id

RELATIONSHIPS:
  orders.customer_id references customers.id
```

---

### Stage 2: Chain-of-Thought Reasoning

**File:** `pipeline/reasoning.py`

Instead of generating SQL directly, the model first creates a step-by-step plan. This improves accuracy by breaking down complex queries.

**Prompt Template:**
```
Given a database schema and a natural language question, break down the query into logical steps.

Question: "Show customers who spent over $1000"

Think step by step:
1. What tables are needed?
2. What columns should be selected?
3. What joins are required?
4. What filters/conditions apply?
5. Are there any aggregations?
```

**Example Reasoning Output:**
```
1. Need the customers table for names and orders table for amounts
2. Select customer name from customers
3. Join orders on orders.customer_id = customers.id
4. Group by customer to sum their orders
5. Filter with HAVING SUM(total) > 1000
```

---

### Stage 3: SQL Generation

**File:** `pipeline/sql_generator.py`

The generator takes the schema + question + reasoning steps and produces SQL. Having the reasoning context helps the model generate more accurate queries.

**Prompt includes:**
- Formatted schema (from Stage 1)
- Original question
- Reasoning steps (from Stage 2)
- Instruction to output only SQL

**Output:**
```sql
SELECT c.name
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
HAVING SUM(o.total) > 1000;
```

---

### Stage 4: Verification & Correction Loop

**File:** `pipeline/verifier.py`

The verifier checks the generated SQL and attempts to fix errors:

1. **Syntax Validation** - Uses `sqlparse` library to check basic SQL syntax
2. **Schema Validation** - Verifies referenced tables/columns exist in the schema
3. **Auto-Correction** - If errors found, asks the LLM to fix them (up to 3 attempts)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Generated   │ --> │   Validate   │ --> │   Valid?     │
│     SQL      │     │   Syntax     │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                           ┌─────────────────────┼─────────────────────┐
                           │ YES                 │                 NO  │
                           ▼                     │                     ▼
                    ┌──────────────┐             │              ┌──────────────┐
                    │   Return     │             │              │  Ask LLM to  │
                    │   Final SQL  │             │              │  Fix Error   │
                    └──────────────┘             │              └──────┬───────┘
                                                 │                     │
                                                 └─────────────────────┘
                                                      (max 3 attempts)
```

---

## Model Details

| Property | Value |
|----------|-------|
| **Model** | Qwen/Qwen2.5-Coder-32B-Instruct |
| **Provider** | HuggingFace Inference API (free tier) |
| **Context** | Schema + Question + Reasoning |
| **Temperature** | 0.1 (low for deterministic SQL) |

### Why This Model?

- **Specialized for code**: Qwen2.5-Coder is trained on programming tasks
- **Instruction-tuned**: Follows prompts accurately
- **Available free**: Works with HuggingFace's free API tier
- **Good SQL performance**: Benchmarks well on text-to-SQL tasks

---

## Project Structure

```
hack/
├── app.py                    # Flask web server
├── config.py                 # Model settings & prompts
├── .env                      # API token (you add this)
├── requirements.txt          # Dependencies
│
├── pipeline/
│   ├── schema_processor.py   # Stage 1: Parse schema
│   ├── reasoning.py          # Stage 2: Chain-of-thought
│   ├── sql_generator.py      # Stage 3: Generate SQL
│   └── verifier.py           # Stage 4: Validate & fix
│
├── utils/
│   └── hf_client.py          # HuggingFace API wrapper
│
├── templates/
│   └── index.html            # Web UI
│
└── static/
    └── styles.css            # UI styling
```

---

## API Endpoint

### POST `/generate`

Generate SQL from natural language.

**Request:**
```json
{
  "schema": "CREATE TABLE users (...);",
  "question": "Show all active users"
}
```

**Response:**
```json
{
  "success": true,
  "sql": "SELECT * FROM users WHERE active = true;",
  "reasoning": "1. Need users table\n2. Select all columns\n3. Filter where active is true",
  "verification": {
    "is_valid": true,
    "corrections_made": 0,
    "notes": []
  }
}
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your HuggingFace token to .env
# Get free token: https://huggingface.co/settings/tokens

# 3. Run
python app.py

# 4. Open http://localhost:5000
```

---

## Customization

Edit `config.py` to:

- **Change model**: Line 18 - try different HuggingFace models
- **Adjust temperature**: Line 26 - higher = more creative, lower = more precise
- **Modify prompts**: Lines 31-77 - customize how the model reasons

---

## Limitations

- Dependent on HuggingFace API availability
- Complex queries with many nested subqueries may be less accurate
- Schema must be provided as valid CREATE TABLE statements
- Free tier has rate limits (may need to wait between requests)

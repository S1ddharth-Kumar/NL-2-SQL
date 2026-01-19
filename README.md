# NL-2-SQL: Natural Language to SQL Pipeline

A modular, interpretable pipeline that converts natural language questions into SQL queries using open-source LLMs via HuggingFace.

## Features

| Requirement | Implementation |
|-------------|----------------|
| Takes natural language questions as input | Web UI with question input and example queries |
| Reasons about the database schema | Chain-of-thought prompting breaks down query logic step-by-step |
| Generates safe, efficient SQL | LLM generates SQL with syntax verification and auto-correction |
| Returns human-readable answers | "In Plain English" section explains what the query does |
| Shows its reasoning | Displays numbered reasoning steps for transparency |
| Security hardened | Multi-layer prompt injection protection |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Flask Web UI                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Security Layer                               │
│         (Input Validation, Prompt Injection Detection)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Pipeline Modules                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Schema     │→ │  Reasoning   │→ │     SQL      │           │
│  │  Processor   │  │   (CoT)      │  │  Generator   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                              │                  │
│                                              ▼                  │
│                    ┌──────────────┐  ┌──────────────┐           │
│                    │   Answer     │← │   Verifier   │           │
│                    │  Generator   │  │ & Corrector  │           │
│                    └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    HuggingFace Inference API
                    (Qwen/Qwen3-Coder-30B-A3B-Instruct)
```

## Pipeline Steps

1. **Security Validation** - Detects prompt injection attempts, sanitizes inputs
2. **Schema Processing** - Parses CREATE TABLE statements to understand database structure
3. **Chain-of-Thought Reasoning** - Breaks down the question into logical steps (tables needed, joins, filters, etc.)
4. **SQL Generation** - Generates SQL based on the reasoning
5. **Verification & Correction** - Validates syntax and schema references, auto-corrects errors
6. **Answer Generation** - Produces a human-readable explanation of what the query does

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure HuggingFace API token:**
   - Get a free token at: https://huggingface.co/settings/tokens
   - Create a `.env` file:
     ```
     HF_API_TOKEN=hf_your_token_here
     ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Benchmarking

The project includes a modular benchmark suite using the [Spider dataset](https://yale-lily.github.io/spider).

### Quick Start

```bash
# Download Spider dataset
python benchmarks/download_spider.py

# Run benchmark (100 samples)
python benchmarks/run_benchmark.py

# With LLM-as-judge semantic evaluation
python benchmarks/run_benchmark.py --llm-judge

# With execution accuracy (requires Spider databases)
python benchmarks/run_benchmark.py --execution --databases-dir benchmarks/spider/database
```

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Exact Match** | Normalized string comparison of SQL |
| **Execution Accuracy** | Compares query results against actual databases |
| **LLM Judge** | Semantic equivalence evaluation via LLM |
| **Valid SQL Rate** | Percentage of syntactically valid SQL generated |

### Sample Results

```
============================================================
BENCHMARK RESULTS (10 samples)
============================================================
  Exact Match:         30.00%
  LLM Judge Match:     42.86%
  Execution Match:     100.00%
  Valid SQL Rate:      70.00%
  Avg Latency:         3,374ms
============================================================
```

### Benchmark Structure

```
benchmarks/
├── run_benchmark.py        # CLI entry point
├── spider_benchmark.py     # Main runner
├── download_spider.py      # Dataset download
├── core/                   # Data classes
│   ├── results.py          # BenchmarkResult, BenchmarkReport
│   ├── data_loader.py      # SpiderDataLoader
│   └── normalizer.py       # SQLNormalizer
└── evaluators/             # Evaluation strategies
    ├── exact_match.py      # String comparison
    ├── execution.py        # Run against SQLite
    └── llm_judge.py        # LLM semantic evaluation
```

## Tech Stack

- **Backend:** Python, Flask
- **LLM:** Qwen/Qwen3-Coder-30B-A3B-Instruct (via HuggingFace Inference API)
- **SQL Parsing:** sqlparse
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Security:** Multi-layer prompt injection detection

## Project Structure

```
├── app.py                    # Flask application
├── config.py                 # Configuration and prompts
├── security.py               # Security layer
├── pipeline/
│   ├── core.py               # Core pipeline class
│   ├── schema_processor.py   # Schema parsing
│   ├── reasoning.py          # Chain-of-thought reasoning
│   ├── sql_generator.py      # SQL generation
│   ├── verifier.py           # Syntax verification
│   └── answer_generator.py   # Human-readable answers
├── benchmarks/               # Benchmark suite
├── tests/                    # Test suite
├── utils/
│   └── hf_client.py          # HuggingFace API client
├── templates/
│   └── index.html            # Web UI
└── static/
    └── styles.css            # Styling
```

## Why No SQL Execution in UI?

We intentionally designed this as a **query generation** tool rather than an execution engine:

1. **Security** - Executing arbitrary SQL poses significant risks
2. **Flexibility** - Users can review/modify SQL before running on their databases
3. **Database Agnostic** - Works with any SQL dialect without needing connections
4. **Educational Focus** - Transparent reasoning helps users understand SQL

## License

MIT License

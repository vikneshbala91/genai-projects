# Trino NL2SQL Project Summary

## 🎯 What It Does

A Flask web application that:
1. Takes natural language questions from users
2. Converts them to Trino SQL queries using Azure OpenAI
3. Executes queries on your Trino database
4. Returns results as both:
   - Plain English explanations
   - Formatted data tables

## 📁 Project Structure

```
trino_nl2sql/
├── src/
│   ├── app.py                    # Main Flask application (port 8080)
│   ├── sql_generator.py          # NL → SQL using Azure OpenAI
│   ├── trino_executor.py         # Execute queries on Trino
│   ├── result_formatter.py       # SQL results → Plain English
│   ├── schema_loader.py          # Load DB schema context
│   ├── templates/
│   │   └── index.html            # Web interface
│   └── static/
│       └── style.css             # UI styling
├── schemas/
│   └── schema_example.yaml       # Database schema definition
├── requirements.txt              # Python dependencies
├── test_setup.py                 # Setup verification script
├── QUICKSTART.md                 # 5-minute start guide
└── README.md                     # Full documentation
```

## 🔧 Core Components

### 1. SQL Generator (`sql_generator.py`)
- **Input**: Natural language question
- **Process**: Uses Azure OpenAI + schema context
- **Output**: Trino-compatible SQL query
- **Temperature**: 0.0 (deterministic)

### 2. Trino Executor (`trino_executor.py`)
- **Input**: SQL query
- **Process**: Executes on Trino cluster
- **Output**: Result rows + column names
- **Features**: HTML/text table formatting

### 3. Result Formatter (`result_formatter.py`)
- **Input**: Question + SQL + Results
- **Process**: Uses Azure OpenAI for natural language
- **Output**: Plain English explanation
- **Temperature**: 0.3 (slightly creative)

### 4. Schema Loader (`schema_loader.py`)
- **Input**: YAML schema file
- **Process**: Parses tables, columns, relationships
- **Output**: Formatted context for LLM

### 5. Flask App (`app.py`)
- **Routes**:
  - `GET /` - Main interface
  - `POST /query` - Process questions
  - `GET /schema` - View database schema
  - `GET /health` - Health check
- **Port**: 8080

## 🔄 Data Flow

```
User Types Question
       ↓
[Schema Loader] → Provides DB context
       ↓
[SQL Generator] → Generates SQL using Azure OpenAI
       ↓
[Trino Executor] → Runs query on Trino
       ↓
[Result Formatter] → Converts to plain English
       ↓
Display: Explanation + SQL + Data Table
```

## ⚙️ Configuration

### Required `.env` Variables

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=your-deployment
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Trino Connection (Required for execution)
TRINO_HOST=localhost
TRINO_PORT=8080
TRINO_USER=admin
TRINO_CATALOG=hive
TRINO_SCHEMA=default
TRINO_HTTP_SCHEME=http
```

### Schema Configuration

Edit `schemas/schema_example.yaml`:

```yaml
database: catalog.schema

tables:
  - name: table_name
    description: What it contains
    columns:
      - name: column_name
        type: bigint
        description: What it stores

relationships:
  - from: table1.id
    to: table2.foreign_id
    description: How they relate
```

## 🚀 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
# Edit .env with your Azure OpenAI credentials
# Edit schemas/schema_example.yaml with your database

# 3. Test Setup
python test_setup.py

# 4. Run
python src/app.py

# 5. Open Browser
# http://localhost:8080
```

## 💡 Example Questions

```
"Show me all customers"
"How many orders were placed last month?"
"What are the top 5 products by price?"
"Show total revenue by category"
"Which customers haven't ordered in 90 days?"
```

## 🎨 UI Features

- **Clean Interface**: Modern, responsive design
- **Real-time Results**: Shows SQL + explanation + data
- **Schema Viewer**: Browse database structure
- **Example Questions**: Quick-start buttons
- **Error Handling**: Clear error messages with SQL

## 🔒 Security Features

- Prevents destructive operations (DROP, DELETE, TRUNCATE)
- SQL validation before execution
- Safe query construction
- No SQL injection vulnerabilities

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Flask (Python) |
| AI | Azure OpenAI (GPT-4) |
| Database | Trino |
| Data Processing | Pandas, Tabulate |
| Config | YAML, dotenv |

## 🧪 Testing

```bash
# Test setup
python test_setup.py

# Test SQL generation only
cd src
python sql_generator.py

# Test Trino connection only
python trino_executor.py
```

## 📝 Key Files Explained

| File | Purpose | Key Features |
|------|---------|--------------|
| `app.py` | Main application | Flask routes, orchestration |
| `sql_generator.py` | NL to SQL | Schema-aware, Trino syntax |
| `trino_executor.py` | Query execution | Connection pooling, formatting |
| `result_formatter.py` | Plain English | Natural explanations |
| `schema_loader.py` | Schema management | YAML parsing, context |
| `index.html` | User interface | Responsive, interactive |
| `style.css` | Styling | Modern, clean design |

## 🔮 Future Enhancements

- [ ] Schema auto-discovery from Trino
- [ ] Query history and favorites
- [ ] Multiple database support
- [ ] Query optimization suggestions
- [ ] Export results (CSV, JSON, Excel)
- [ ] User authentication
- [ ] Query caching
- [ ] Streaming results for large datasets

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect to Trino | Check TRINO_HOST and credentials |
| SQL generation fails | Verify Azure OpenAI config |
| Wrong SQL generated | Update schema.yaml with accurate info |
| Port 8080 in use | Change port in app.py |
| Missing modules | Run `pip install -r requirements.txt` |

## 📚 Documentation

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - This file
- `schemas/schema_example.yaml` - Schema format reference

## 🎯 Use Cases

1. **Data Analysts**: Query databases without writing SQL
2. **Business Users**: Get insights in plain English
3. **Developers**: Rapid prototyping and testing
4. **Data Teams**: Self-service analytics
5. **Executives**: Quick data exploration

## ⚡ Performance Notes

- SQL generation: ~2-3 seconds
- Query execution: Depends on Trino cluster
- Result formatting: ~1-2 seconds
- Total time: Typically 5-10 seconds

## 📞 Support

- Check logs in terminal for debugging
- Review generated SQL before trusting results
- Test with simple queries first
- Ensure schema file is accurate

---

Built with ❤️ using Flask, LangChain, and Azure OpenAI

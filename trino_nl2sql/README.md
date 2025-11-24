# Trino NL2SQL - Natural Language to SQL Query Interface

A Flask web application that converts natural language questions into SQL queries, executes them on Trino, and presents results in both plain English and data tables.

## Features

- 🗣️ **Natural Language Interface**: Ask questions in plain English
- 🔍 **SQL Generation**: Automatically generates Trino-compatible SQL queries
- ⚡ **Query Execution**: Executes queries on your Trino cluster
- 📊 **Smart Results**: Presents results as both explanations and data tables
- 📚 **Schema Aware**: Uses your database schema for accurate query generation
- 🎨 **Modern UI**: Clean, responsive web interface

## Architecture

```
User Question → SQL Generator → Trino Executor → Result Formatter → User
                     ↓
              Schema Context
```

## Project Structure

```
trino_nl2sql/
├── src/
│   ├── app.py                # Main Flask application
│   ├── sql_generator.py      # NL to SQL conversion
│   ├── trino_executor.py     # Trino query execution
│   ├── result_formatter.py   # Plain English explanations
│   ├── schema_loader.py      # Database schema management
│   ├── templates/
│   │   └── index.html        # Web interface
│   └── static/
│       └── style.css         # Styling
├── schemas/
│   └── schema_example.yaml   # Database schema definition
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup

### 1. Install Dependencies

```bash
cd trino_nl2sql
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add these to your `.env` file in the project root:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=your-deployment-name

# Trino Configuration
TRINO_HOST=your-trino-host
TRINO_PORT=8080
TRINO_USER=your-username
TRINO_CATALOG=your-catalog
TRINO_SCHEMA=your-schema
TRINO_HTTP_SCHEME=http  # or https
```

### 3. Configure Your Database Schema

Edit `schemas/schema_example.yaml` with your actual database schema:

```yaml
database: my_catalog.my_schema

tables:
  - name: customers
    description: Customer information
    columns:
      - name: customer_id
        type: bigint
        description: Unique identifier
      # ... more columns
```

The schema helps the AI understand your database structure for accurate SQL generation.

### 4. Run the Application

```bash
cd src
python app.py
```

Or from anywhere:
```bash
python trino_nl2sql/src/app.py
```

The application will be available at **http://localhost:8080**

## Usage

### Web Interface

1. Open http://localhost:8080 in your browser
2. Type a question in plain English (e.g., "Show me top 10 customers by revenue")
3. Click "Ask Question" or press Enter
4. View the results:
   - Plain English explanation
   - Generated SQL query
   - Data table with results

### Example Questions

- "Show me all customers"
- "How many orders were placed last month?"
- "What are the top 5 products by price?"
- "Show total revenue by category"
- "Which customers haven't ordered in the last 3 months?"

### Viewing Schema

Click the "View Schema" button to see your database structure. This helps you understand what questions you can ask.

## Components

### 1. SQL Generator (`sql_generator.py`)
- Converts natural language to Trino SQL
- Uses Azure OpenAI with schema context
- Ensures Trino-compatible syntax

### 2. Trino Executor (`trino_executor.py`)
- Connects to Trino cluster
- Executes SQL queries safely
- Formats results as tables

### 3. Result Formatter (`result_formatter.py`)
- Converts query results to plain English
- Highlights key findings
- Makes data accessible to non-technical users

### 4. Schema Loader (`schema_loader.py`)
- Loads database schema from YAML
- Provides context to SQL generator
- Helps generate accurate queries

## Configuration

### Schema Configuration

The schema file (`schemas/schema_example.yaml`) defines:

- **Tables**: Names and descriptions
- **Columns**: Names, types, and descriptions
- **Relationships**: Foreign key relationships
- **Database**: Catalog and schema names

This information helps the AI generate accurate SQL queries.

### Customization

You can customize:

1. **Port**: Change in `app.py` (default: 8080)
2. **Temperature**: Adjust in `sql_generator.py` for more/less creative queries
3. **Result Limit**: Modify SQL generation prompt for default limits
4. **UI Theme**: Edit `static/style.css`

## Security Notes

- The system prevents destructive operations (DROP, DELETE, TRUNCATE)
- Uses parameterized queries where possible
- Review generated SQL before using in production
- Use appropriate Trino user permissions

## Troubleshooting

### Common Issues

**"No module named..."**
- Make sure all dependencies are installed: `pip install -r requirements.txt pyyaml`

**"Failed to connect to Trino"**
- Check Trino connection settings in `.env`
- Verify Trino cluster is running and accessible
- Test connection manually: `trino --server <host>:<port>`

**"Failed to generate SQL"**
- Verify Azure OpenAI credentials in `.env`
- Check deployment name matches your Azure resource
- Ensure schema file is properly formatted

**Empty or incorrect results**
- Update schema file with accurate table/column information
- Provide more specific questions
- Check Trino query logs for actual executed SQL

## Development

### Adding New Features

1. **Custom SQL Functions**: Add examples to `sql_generator.py` prompt
2. **New Result Formats**: Extend `trino_executor.py` formatting methods
3. **Schema Auto-Discovery**: Connect to Trino and query information_schema

### Testing

Test individual components:

```bash
# Test SQL generation
cd src
python sql_generator.py

# Test Trino connection
python trino_executor.py
```

## License

MIT

## Support

For issues or questions, check:
- Trino documentation: https://trino.io/docs/
- LangChain docs: https://python.langchain.com/
- Azure OpenAI: https://learn.microsoft.com/azure/ai-services/openai/

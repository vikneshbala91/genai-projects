# Quick Start Guide - Trino NL2SQL

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Access to Azure OpenAI
- Trino cluster (optional for testing - can use mock mode)

## Step 1: Install Dependencies

```bash
cd trino_nl2sql
pip install -r requirements.txt
```

## Step 2: Configure Your Schema

Edit `schemas/schema_example.yaml` with your actual database tables:

```yaml
database: my_catalog.my_schema

tables:
  - name: my_table
    description: What this table contains
    columns:
      - name: id
        type: bigint
        description: Primary key
      # Add more columns...
```

## Step 3: Update Environment Variables

The `.env` file in the project root already has placeholders. Update these values:

```bash
# Azure OpenAI (required)
AZURE_OPENAI_API_KEY="your-actual-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT="your-deployment-name"

# Trino Connection (update with your values)
TRINO_HOST="your-trino-host"
TRINO_PORT=8080
TRINO_USER="your-username"
TRINO_CATALOG="your-catalog"
TRINO_SCHEMA="your-schema"
```

## Step 4: Run the Application

```bash
cd src
python app.py
```

Or from anywhere:
```bash
python trino_nl2sql/src/app.py
```

## Step 5: Open in Browser

Navigate to: **http://localhost:8080**

## Try It Out!

1. Click "View Schema" to see your database structure
2. Type a question: "Show me all records from my_table"
3. Click "Ask Question" or press Enter
4. View the results!

## Example Questions

Based on the example schema:

- "Show me all customers"
- "How many orders were placed last month?"
- "What are the top 5 products by price?"
- "Show customers who haven't ordered in 30 days"
- "What is the total revenue by product category?"

## Troubleshooting

### Can't connect to Trino?

The app will still generate SQL! You can:
1. Copy the generated SQL
2. Test it manually on your Trino cluster
3. Fix connection settings later

### SQL looks wrong?

1. Check your schema file is accurate
2. Be more specific in your question
3. Review the generated SQL and adjust your question

### Azure OpenAI errors?

- Verify your deployment name exists
- Check API key is correct
- Ensure you have quota available

## Next Steps

- Customize the schema with your actual tables
- Add more example questions
- Integrate with your Trino cluster
- Deploy to production

## Architecture Flow

```
Your Question
    ↓
[SQL Generator] → reads schema context
    ↓
Generated SQL Query
    ↓
[Trino Executor] → executes on your cluster
    ↓
Query Results
    ↓
[Result Formatter] → converts to plain English
    ↓
Display: Explanation + Data Table
```

## Key Files

- `src/app.py` - Main Flask application
- `schemas/schema_example.yaml` - Your database schema
- `.env` - Configuration (in project root)
- `src/sql_generator.py` - NL to SQL conversion
- `src/trino_executor.py` - Query execution

## Tips

1. **Be Specific**: "Show top 10 customers by revenue in 2024" is better than "show customers"
2. **Check Schema**: Use "View Schema" to see what's available
3. **Review SQL**: Always check the generated SQL before relying on results
4. **Iterate**: If results aren't right, rephrase your question
5. **Start Simple**: Test with simple queries first

## Support

- Check the full [README.md](README.md) for detailed documentation
- Review example schema in `schemas/schema_example.yaml`
- Test SQL generation without Trino connection

Happy querying! 🚀

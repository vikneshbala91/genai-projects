# Dynamic Schema Fetching

## Overview

The application now supports **dynamic schema fetching from Trino** combined with **business descriptions from YAML**. This gives you the best of both worlds:

- **Automatic schema discovery**: Tables, columns, and data types are fetched directly from Trino
- **Business context**: Add meaningful descriptions in YAML to help the LLM understand your data

## How It Works

### 1. Dynamic Schema Fetching

The system automatically:
- Connects to Trino using credentials from your `.env` file
- Fetches all tables from the specified `TRINO_CATALOG.TRINO_SCHEMA`
- Gets column names, data types, and any comments from Trino
- Builds a complete schema representation

### 2. Business Descriptions (Optional)

You can optionally provide business context in a YAML file:
- Describe what tables represent in business terms
- Add meaningful descriptions for columns (e.g., "User's primary email for login")
- Define relationships between tables
- Add business rules and conventions

### 3. Merging

The system merges both sources:
- **Structure from Trino**: Always uses actual table names, column names, and data types
- **Descriptions from YAML**: Adds business context where provided
- **Fallback**: If Trino is unavailable, falls back to YAML-only mode

## Setup

### Step 1: Configure Environment Variables

Ensure your `.env` file has these settings:

```bash
# Trino Connection
TRINO_HOST=your-trino-host.com
TRINO_PORT=443
TRINO_USER=your_username
TRINO_PASSWORD=your_password
TRINO_CATALOG=hive          # Your target catalog
TRINO_SCHEMA=reco_prod      # Your target schema
TRINO_HTTP_SCHEME=https
```

### Step 2: Add Business Descriptions (Optional)

Edit `schemas/business_descriptions.yaml`:

```yaml
tables:
  - name: user_events
    description: Tracks all user interactions with the platform
    columns:
      - name: event_type
        description: Type of event - possible values are 'click', 'view', 'purchase', 'signup'
      - name: user_id
        description: Foreign key to users table. Can be null for anonymous events.

relationships:
  - from: user_events.user_id
    to: users.id
    description: Each event may be associated with a registered user
```

**Important**: You only need to add entries for tables/columns that need business context. You don't need to list every table or column - the system will fetch those from Trino automatically.

### Step 3: Test the Connection

Run the test script to verify everything is working:

```bash
python test_dynamic_schema.py
```

This will:
- Test dynamic schema fetching from Trino
- Show you all discovered tables and columns
- Display the merged schema context that will be sent to the LLM
- Test fallback to YAML-only mode

## Usage

### In Code

```python
from schema_loader import SchemaLoader

# Use dynamic schema (recommended)
loader = SchemaLoader(use_dynamic_schema=True)

# Get schema context for LLM
schema_context = loader.get_schema_context()

# Get list of tables
tables = loader.get_table_names()

# Get database name
db_name = loader.get_database_name()
```

### Custom Business Descriptions File

```python
from schema_loader import SchemaLoader

# Use a custom YAML file for business descriptions
loader = SchemaLoader(
    schema_file="path/to/custom_descriptions.yaml",
    use_dynamic_schema=True
)
```

### Disable Dynamic Fetching (YAML only)

```python
from schema_loader import SchemaLoader

# Use only YAML, don't connect to Trino
loader = SchemaLoader(use_dynamic_schema=False)
```

## Benefits

### Dynamic Schema Fetching
✅ Always up-to-date with your database
✅ No manual maintenance of schema files
✅ Automatically discovers new tables and columns
✅ Uses actual data types from Trino

### Business Descriptions
✅ Helps LLM understand data meaning
✅ Improves SQL generation accuracy
✅ Documents business logic and conventions
✅ Only add descriptions where needed

## Workflow for Adding New Tables

When you add a new table to Trino:

1. **Nothing required!** The system will automatically discover it
2. **(Optional)** Add business descriptions to YAML if the table/column names aren't self-explanatory

Example:
```yaml
tables:
  - name: usr_evt_log
    description: User event log - tracks all user interactions
    columns:
      - name: evt_typ
        description: Event type code. 1=click, 2=view, 3=purchase
      - name: ts
        description: Event timestamp in UTC
```

## Troubleshooting

### "Failed to load dynamic schema"

**Cause**: Can't connect to Trino
**Solution**:
- Check your `.env` file has correct credentials
- Test connection with `python test_connection.py`
- Verify `TRINO_CATALOG` and `TRINO_SCHEMA` exist in your Trino instance

**Fallback**: System automatically falls back to YAML-only mode

### "No tables found"

**Cause**: The specified catalog.schema is empty or doesn't exist
**Solution**:
- Verify `TRINO_CATALOG` and `TRINO_SCHEMA` in `.env`
- Run `SHOW SCHEMAS FROM your_catalog` in Trino to see available schemas
- Check you have permissions to access the schema

### Empty descriptions

**Cause**: No YAML descriptions provided and Trino table has no comments
**Solution**: Add descriptions to `business_descriptions.yaml` for better LLM understanding

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SQL Generator                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Schema Loader                          │
│  ┌────────────────────┐         ┌─────────────────────────┐│
│  │  Trino Schema      │         │  YAML Descriptions      ││
│  │  Fetcher           │         │  (Business Context)     ││
│  │                    │         │                         ││
│  │  - Tables          │  Merge  │  - Table descriptions   ││
│  │  - Columns         │   ───►  │  - Column descriptions  ││
│  │  - Data Types      │         │  - Relationships        ││
│  │  - Comments        │         │  - Business Rules       ││
│  └────────────────────┘         └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Schema Context for LLM
```

## Files

- `src/trino_schema_fetcher.py` - Fetches schema from Trino
- `src/schema_loader.py` - Merges Trino schema with YAML descriptions
- `schemas/business_descriptions.yaml` - Business context (optional)
- `schemas/schema_example.yaml` - Old static schema (kept for fallback)
- `test_dynamic_schema.py` - Test script to verify setup

## Migration from Static Schema

If you were using the old static `schema_example.yaml`:

1. The system still works! It falls back to YAML if Trino is unavailable
2. Extract just the business descriptions from your YAML
3. Remove the data types (they'll come from Trino)
4. Move descriptions to `business_descriptions.yaml`
5. Configure `.env` with Trino connection details

## Next Steps

1. ✅ Configure your `.env` file with Trino credentials
2. ✅ Run `python test_dynamic_schema.py` to verify
3. ✅ Add business descriptions to `schemas/business_descriptions.yaml`
4. ✅ Start using natural language queries!

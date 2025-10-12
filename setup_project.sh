#!/bin/bash

# Setup script for GenAI subprojects
# Usage: ./setup_project.sh <project_name>

set -e

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./setup_project.sh <project_name>"
    echo "Example: ./setup_project.sh my_new_project"
    exit 1
fi

if [ -d "$PROJECT_NAME" ]; then
    echo "Project '$PROJECT_NAME' already exists!"
    read -p "Do you want to set up the virtual environment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "Creating new project: $PROJECT_NAME"
    mkdir -p "$PROJECT_NAME/src"

    # Create README
    cat > "$PROJECT_NAME/README.md" << EOF
# $PROJECT_NAME

[Add a brief description of what this project does]

## Setup

1. Create and activate virtual environment:
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

## Usage

[Add usage instructions here]

## Dependencies

See [requirements.txt](requirements.txt) for a full list of dependencies.

## Development

To add new dependencies:
\`\`\`bash
pip install package-name
pip freeze > requirements.txt
\`\`\`
EOF

    # Create requirements.txt
    cat > "$PROJECT_NAME/requirements.txt" << EOF
# Add your project dependencies here
# Example:
# numpy==1.24.0
# pandas==2.0.0
# openai==1.0.0
EOF

    # Create __init__.py
    echo "# $PROJECT_NAME Package" > "$PROJECT_NAME/src/__init__.py"

    echo "Project structure created!"
fi

# Set up virtual environment
cd "$PROJECT_NAME"

if [ -d "venv" ]; then
    echo "Virtual environment already exists in $PROJECT_NAME/venv"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  cd $PROJECT_NAME"
echo "  source venv/bin/activate  # macOS/Linux"
echo "  # or"
echo "  venv\\Scripts\\activate  # Windows"
echo ""
echo "Then install dependencies:"
echo "  pip install -r requirements.txt"

# GenAI Projects

A collection of GenAI subprojects, each with isolated dependencies and virtual environments.

## Project Structure

```
genai-projects/
├── factcheck_sidekick/
│   ├── venv/              # Virtual environment (git-ignored)
│   ├── requirements.txt   # Project dependencies
│   ├── src/              # Source code
│   └── README.md         # Project-specific documentation
└── [other_subprojects]/
```

## Quick Start

### Setting Up a New Subproject

1. Create a new subproject folder:
   ```bash
   mkdir my_project
   cd my_project
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # macOS/Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

4. Create and install dependencies:
   ```bash
   # Create requirements.txt with your dependencies
   echo "your-package==version" > requirements.txt

   # Install dependencies
   pip install -r requirements.txt
   ```

5. Save your current environment:
   ```bash
   pip freeze > requirements.txt
   ```

### Working with Existing Subprojects

1. Navigate to the subproject:
   ```bash
   cd factcheck_sidekick
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Subprojects

### factcheck_sidekick
Description: [Add description here]

## Best Practices

1. **Always activate the venv** before installing packages
2. **Update requirements.txt** after installing new packages: `pip freeze > requirements.txt`
3. **Keep venvs isolated** - don't share venv folders between projects
4. **Document dependencies** in each subproject's README.md

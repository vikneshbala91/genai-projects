# Debugging Guide for Fact-Check Sidekick

This guide shows you where to set breakpoints to monitor tool invocations and outputs.

## Key Breakpoint Locations in app.py

### 1. **Incoming User Messages** (Line ~130)
```python
logger.info(f"📨 NEW USER MESSAGE: {user_message}")
# BREAKPOINT HERE: Set breakpoint on this line to see incoming messages
```
**What you'll see:** The user's incoming message before processing

---

### 2. **Tool Invocation Start** (Line ~46)
```python
logger.info(f"🔧 TOOL INVOKED: {tool_name}")
logger.info(f"📥 INPUT: {input_str}")
# BREAKPOINT HERE: Set breakpoint on this line to catch tool invocations
```
**What you'll see:**
- Which tool is being called (e.g., `web_search`, `read_url`)
- The input parameters being passed to the tool

---

### 3. **Tool Output** (Line ~54)
```python
logger.info(f"✅ TOOL OUTPUT:")
# BREAKPOINT HERE: Set breakpoint on this line to see tool outputs
```
**What you'll see:**
- The output returned by the tool
- Search results, webpage content, etc.

---

### 4. **Tool Errors** (Line ~61)
```python
logger.error(f"❌ TOOL ERROR: {error}")
# BREAKPOINT HERE: Set breakpoint on this line to catch tool errors
```
**What you'll see:** Any errors that occur during tool execution

---

### 5. **Agent Decision Making** (Line ~67)
```python
logger.info(f"🤖 AGENT ACTION: {action.tool}")
logger.info(f"📋 Action Input: {action.tool_input}")
# BREAKPOINT HERE: Set breakpoint on this line to see agent decisions
```
**What you'll see:**
- Which tool the agent decides to use
- The reasoning behind tool selection

---

### 6. **Final Agent Response** (Line ~140)
```python
result = executor.invoke(...)
# BREAKPOINT HERE: Set breakpoint on this line to see final results
```
**What you'll see:** The complete result object with all intermediate steps

---

### 7. **Agent Response Text** (Line ~145)
```python
logger.info(f"🤖 AGENT RESPONSE: {response_text}")
```
**What you'll see:** The final response sent back to the user

---

## How to Set Breakpoints in VS Code

1. **Open app.py** in VS Code
2. **Click on the left margin** (next to the line number) where you want to pause execution
3. A **red dot** will appear indicating a breakpoint
4. **Run the app in debug mode**:
   - Press `F5` or click "Run and Debug" in the sidebar
   - Select "Python File" or create a launch configuration

## VS Code Debug Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask: Fact-Check Sidekick",
            "type": "debugpy",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--host=0.0.0.0",
                "--port=9000"
            ],
            "jinja": true,
            "cwd": "${workspaceFolder}/factcheck_sidekick/src"
        }
    ]
}
```

## Alternative: Using Print/Logging

If you prefer logging over breakpoints, the app already includes comprehensive logging:

```bash
# Run the app and watch the logs
cd factcheck_sidekick/src
python app.py
```

The logs will show:
- 📨 User messages
- 🔧 Tool invocations
- 📥 Tool inputs
- ✅ Tool outputs
- 🤖 Agent responses
- ❌ Any errors

## Inspecting Variables at Breakpoints

When stopped at a breakpoint, you can inspect:

| Variable | Description |
|----------|-------------|
| `user_message` | The user's input |
| `tool_name` | Name of the tool being invoked |
| `input_str` | Input parameters for the tool |
| `output` | Output from the tool |
| `action.tool` | Which tool the agent chose |
| `action.tool_input` | Input the agent is passing |
| `result` | Complete agent execution result |
| `response_text` | Final response to user |

## Common Debugging Scenarios

### Scenario 1: Tool Not Being Called
**Set breakpoint at:** Line 67 (Agent Action)
**Check:** Is the agent deciding to use the tool? What's in `action.tool_input`?

### Scenario 2: Tool Returning Empty/Wrong Results
**Set breakpoint at:** Line 54 (Tool Output)
**Check:** What's the actual output? Is it formatted correctly?

### Scenario 3: Agent Not Using Search Results
**Set breakpoints at:** Lines 46, 54, and 140
**Check:** Are tools being called? Are outputs being passed to the next step?

### Scenario 4: Error in Tool Execution
**Set breakpoint at:** Line 61 (Tool Error)
**Check:** What's the error message? Which tool failed?

## Tips

1. **Use conditional breakpoints** - Right-click on a breakpoint to add conditions
   - Example: Only break when `tool_name == "web_search"`

2. **Watch expressions** - Add variables to the Watch panel to track them across breakpoints

3. **Step through code** - Use F10 (step over) and F11 (step into) to follow execution

4. **Call stack** - Check the call stack panel to see how you got to the current point

5. **Debug Console** - Evaluate expressions and inspect variables interactively

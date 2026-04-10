import subprocess
import os
import uuid
import re

def execute_code(script: str, timeout=10) -> str:
    """Run python code securely via subprocess and return stdout/stderr."""
    script_id = str(uuid.uuid4())[:8]
    filename = f"temp_sandbox_{script_id}.py"
    
    try:
        with open(filename, "w") as f:
            f.write(script)
            
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
            
        if not output.strip():
            return "[Code executed successfully with no output]"
        return output[:2000] # Cap output limit
        
    except subprocess.TimeoutExpired:
        return f"CRITICAL: Script execution exceeded {timeout} seconds timeout limit."
    except Exception as e:
        return f"Sandbox exception: {e}"
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def extract_code(text: str) -> str:
    """Extract code from markdown blocks."""
    match = re.search(r'```(?:python)?(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

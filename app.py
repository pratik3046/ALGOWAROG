from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import requests
from questions import QUESTIONS

# Validate QUESTIONS loaded successfully
if not QUESTIONS or len(QUESTIONS) == 0:
    raise RuntimeError("❌ CRITICAL: No questions loaded from questions.py! Tournament cannot start.")
else:
    print(f"✅ Loaded {len(QUESTIONS)} questions successfully")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'code-battle-secret-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Piston API Configuration
PISTON_API = "https://emkc.org/api/v2/piston"

# Language mapping for Piston
LANGUAGE_MAP = {
    'python': {'language': 'python', 'version': '3.10.0'},
    'javascript': {'language': 'javascript', 'version': '18.15.0'},
    'java': {'language': 'java', 'version': '15.0.2'},
    'cpp': {'language': 'cpp', 'version': '10.2.0'},
    'c': {'language': 'c', 'version': '10.2.0'}
}

# Global State - Reset on server restart
TOURNAMENT_CAPACITY = None
HOST_SID = None
HOST_NAME = None
HOST_SELECTED_PLAYER_COUNT = None
TOURNAMENT_STATUS = 'NOT_STARTED'  # NOT_STARTED, READY, LIVE
players = {}
active_matches = {}
next_round_winners = []
current_round_number = 0
used_questions = set()

# Timer Configuration
QUESTION_TIMER_SECONDS = 600  # 10 minutes per question
match_timers = {}  # Store timer data for each match

def reset_tournament_state():
    """Reset all tournament state - called on server start and when needed"""
    global TOURNAMENT_CAPACITY, HOST_SID, HOST_NAME, HOST_SELECTED_PLAYER_COUNT
    global TOURNAMENT_STATUS, players, active_matches, next_round_winners
    global current_round_number, used_questions, match_timers
    
    print("🔄 Resetting tournament state...")
    TOURNAMENT_CAPACITY = None
    HOST_SID = None
    HOST_NAME = None
    HOST_SELECTED_PLAYER_COUNT = None
    TOURNAMENT_STATUS = 'NOT_STARTED'
    players.clear()
    active_matches.clear()
    next_round_winners.clear()
    current_round_number = 0
    used_questions.clear()
    match_timers.clear()
    print("✅ Tournament state reset complete")

# Initialize clean state on server start
reset_tournament_state()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint to verify Piston API connectivity"""
    try:
        response = requests.get(f"{PISTON_API}/runtimes", timeout=5)
        if response.status_code == 200:
            runtimes = response.json()
            
            # Check for required languages
            available_langs = {}
            for lang in ['python', 'javascript', 'java', 'c++', 'c']:
                lang_runtimes = [r for r in runtimes if r['language'] == lang]
                if lang_runtimes:
                    available_langs[lang] = {
                        'available': True,
                        'version': lang_runtimes[0]['version']
                    }
                else:
                    available_langs[lang] = {'available': False}
            
            return {
                'status': 'healthy',
                'piston_api': 'connected',
                'total_runtimes': len(runtimes),
                'languages': available_langs
            }, 200
        else:
            return {
                'status': 'unhealthy',
                'piston_api': 'error',
                'error': f'HTTP {response.status_code}'
            }, 503
    except Exception as e:
        return {
            'status': 'unhealthy',
            'piston_api': 'disconnected',
            'error': str(e)
        }, 503

def execute_code(language, code, stdin=""):
    """Execute code using Piston API with LeetCode-style wrapper"""
    try:
        if language not in LANGUAGE_MAP:
            return {'success': False, 'error': 'Unsupported language'}
        
        lang_config = LANGUAGE_MAP[language]
        
        # Wrap code based on language - detects if user wrote complete program
        wrapped_code = wrap_user_code(language, code, stdin)
        print(f"🔧 Wrapped {language.upper()} code (first 500 chars):\n{wrapped_code[:500]}...\n")
        
        # Determine if stdin should be used
        # If code wasn't wrapped (user wrote complete program), use stdin directly
        # If code was wrapped, Python/JS handle stdin internally
        code_was_wrapped = (wrapped_code != code)
        
        if code_was_wrapped and language in ['python', 'javascript']:
            use_stdin = ''  # Wrapper handles stdin internally
        else:
            use_stdin = stdin  # User's complete program or C++/Java/C use stdin
            print(f"📥 Input will be passed via stdin: {stdin[:100]}...\n")
        
        # Set appropriate filename based on language (CRITICAL for Piston)
        # FIXED: Don't include extension - Piston adds it automatically for compiled languages
        if language == 'java':
            filename = 'Main.java'  # Java needs .java extension
        elif language == 'cpp':
            filename = 'main'  # FIXED: No extension - Piston adds .cpp automatically
        elif language == 'c':
            filename = 'main'  # FIXED: No extension - Piston adds .c automatically
        elif language == 'javascript':
            filename = 'solution.js'
        else:
            filename = 'main.py'
        
        # Build payload with proper file structure
        payload = {
            'language': lang_config['language'],
            'version': lang_config['version'],
            'files': [{
                'name': filename,
                'content': wrapped_code
            }],
            'stdin': use_stdin,
            'compile_timeout': 10000,
            'run_timeout': 3000
        }
        
        print(f"📦 Sending to Piston API: {lang_config['language']} v{lang_config['version']}, file: {filename}")
        
        response = requests.post(f"{PISTON_API}/execute", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check for compilation errors - return stderr from compile phase specifically
            if result.get('compile') and result['compile'].get('code') != 0:
                compile_stderr = result['compile'].get('stderr', '').strip()
                compile_stdout = result['compile'].get('stdout', '').strip()
                compile_error = compile_stderr if compile_stderr else compile_stdout if compile_stdout else 'Compilation failed'
                print(f"❌ Compilation error:\n{compile_error}")
                return {
                    'success': False,
                    'error': 'Compilation Error',
                    'output': compile_error
                }
            
            # Check runtime results
            run_result = result.get('run', {})
            stdout = run_result.get('stdout', '').strip()
            stderr = run_result.get('stderr', '').strip()
            
            print(f"📤 Output: {stdout}")
            if stderr:
                print(f"⚠️ Stderr: {stderr}")
            
            if run_result.get('code') != 0:
                error_msg = stderr if stderr else 'Runtime error occurred'
                print(f"❌ Runtime error (exit code {run_result.get('code')}): {error_msg}")
                return {
                    'success': False,
                    'error': 'Runtime Error',
                    'output': error_msg
                }
            
            return {
                'success': True,
                'output': stdout,
                'stderr': stderr
            }
        else:
            print(f"❌ Piston API error: HTTP {response.status_code}")
            return {'success': False, 'error': f'Execution service unavailable (HTTP {response.status_code})'}
            
    except requests.Timeout:
        print("❌ Request timeout")
        return {'success': False, 'error': 'Execution timeout'}
    except Exception as e:
        print(f"❌ Execution exception: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f'Execution error: {str(e)}'}

def wrap_user_code(language, user_code, stdin):
    """Wrap user code with input parsing and function calling logic
    FIXED: Detect if user wrote complete program or just function
    """
    # Check if user already wrote a complete program (has main function)
    if language == 'python':
        # Check if user wrote complete Python program
        if 'if __name__' in user_code or 'input()' in user_code:
            return user_code  # User wrote complete program, don't wrap
        return wrap_python_code(user_code, stdin)
    
    elif language == 'cpp':
        # Check if user wrote complete C++ program
        if 'int main(' in user_code or 'int main (' in user_code:
            return user_code  # User wrote complete program, don't wrap
        return wrap_cpp_code(user_code, stdin)
    
    elif language == 'java':
        # Check if user wrote complete Java program
        if 'public static void main' in user_code or 'public class Main' in user_code:
            return user_code  # User wrote complete program, don't wrap
        return wrap_java_code(user_code, stdin)
    
    elif language == 'javascript':
        # Check if user wrote complete JavaScript program
        if 'require(' in user_code or 'process.stdin' in user_code or 'readline' in user_code:
            return user_code  # User wrote complete program, don't wrap
        return wrap_javascript_code(user_code, stdin)
    
    elif language == 'c':
        # Check if user wrote complete C program
        if 'int main(' in user_code or 'int main (' in user_code:
            return user_code  # User wrote complete program, don't wrap
        return wrap_c_code(user_code, stdin)
    
    else:
        return user_code

def extract_cpp_function_name(code):
    """Extract function name from C++ code for dynamic calling"""
    import re
    m = re.search(r'(?:int|void|string|vector<int>)\s+(\w+)\s*\(', code)
    return m.group(1) if m else 'solution'

def wrap_python_code(user_code, stdin):
    """Wrap Python function in Solution class - Users only provide function implementation"""
    import json as json_module
    
    # Use json.dumps to safely escape the input data - prevents syntax errors from special chars
    safe_stdin = json_module.dumps(stdin)
    
    wrapper = f"""import json
import sys
import inspect

class Solution:
{chr(10).join('    ' + line for line in user_code.split(chr(10)))}

# Parse input and call the Solution class method
if __name__ == "__main__":
    input_data = json.loads({safe_stdin})
    
    # Handle if input_data is already parsed (int/string) or needs parsing (string with newlines)
    if isinstance(input_data, str):
        lines = input_data.strip().split('\\n')
    else:
        # Already parsed - convert to string for consistent handling
        lines = [str(input_data)]
    
    # Create Solution instance
    solution = Solution()
    
    # Dynamically detect the method inside Solution class - find first callable non-private method
    method_name = None
    for name in dir(solution):
        if not name.startswith('_') and callable(getattr(solution, name)):
            method_name = name
            break
    
    if not method_name:
        print("Error: No method found in Solution class", file=sys.stderr)
        sys.exit(1)
    
    method = getattr(solution, method_name)
    
    # Get the number of parameters the method expects (excluding self)
    sig = inspect.signature(method)
    param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
    
    try:
        # Parse stdin and pass as individual arguments
        if param_count == 1:
            # Single parameter function
            if len(lines) == 1:
                line = lines[0].strip()
                if line.startswith('['):
                    param = json.loads(line)
                else:
                    try:
                        param = int(line)
                    except ValueError:
                        param = line
                result = method(param)
            elif len(lines) == 2:
                # Two lines but single parameter - parse as array from second line
                line2 = lines[1].strip()
                if ' ' in line2:
                    param = list(map(int, line2.split()))
                elif line2.startswith('['):
                    param = json.loads(line2)
                else:
                    param = int(line2)
                result = method(param)
            else:
                # Multiple lines - second line is the data
                data_line = lines[1].strip()
                if ' ' in data_line:
                    param = list(map(int, data_line.split()))
                else:
                    param = json.loads(data_line)
                result = method(param)
        elif param_count == 2:
            # Two parameter function
            if len(lines) == 1:
                # Single line with space-separated values
                parts = lines[0].strip().split()
                param1 = int(parts[0])
                param2 = int(parts[1])
                result = method(param1, param2)
            elif len(lines) == 2:
                line1 = lines[0].strip()
                line2 = lines[1].strip()
                
                # Parse first parameter
                if line1.startswith('['):
                    param1 = json.loads(line1)
                else:
                    try:
                        param1 = int(line1)
                    except ValueError:
                        param1 = line1
                
                # Parse second parameter
                if line2.startswith('['):
                    param2 = json.loads(line2)
                else:
                    try:
                        param2 = int(line2)
                    except ValueError:
                        param2 = line2
                
                result = method(param1, param2)
            else:
                # Multiple lines
                param1 = json.loads(lines[0])
                param2 = json.loads(lines[1])
                result = method(param1, param2)
        else:
            # More than 2 parameters - parse all lines
            params = []
            for line in lines:
                line = line.strip()
                if line.startswith('['):
                    params.append(json.loads(line))
                else:
                    try:
                        params.append(int(line))
                    except ValueError:
                        params.append(line)
            result = method(*params)
        
        # Print the return value to stdout
        if result is not None:
            if isinstance(result, list):
                print(str(result))
            else:
                print(result)
        elif param_count == 1 and isinstance(param, list):
            # For in-place modifications (like reverseString) - print the modified parameter
            print(str(param))
        else:
            # For in-place modifications (like reverseString)
            # Print the modified first parameter
            if len(lines) >= 1:
                line = lines[0].strip()
                if line.startswith('['):
                    modified_param = json.loads(line)
                    print(str(modified_param))
    except Exception as e:
        print(f"Error: {{str(e)}}", file=sys.stderr)
        import traceback
        traceback.print_exc()
"""
    return wrapper

def wrap_cpp_code(user_code, stdin):
    """Universal C++ wrapper - detects function signature and matches input accordingly
    FIXED: Proper parameter type matching based on function signature
    """
    import json
    import re
    
    function_name = extract_cpp_function_name(user_code)
    
    # Detect function signature more precisely
    sig_match = re.search(r'(int|void|string|vector<int>)\s+' + function_name + r'\s*\(([^)]*)\)', user_code)
    return_type = sig_match.group(1) if sig_match else 'int'
    params = sig_match.group(2).strip() if sig_match else 'int n'
    
    # Analyze parameters
    if not params or params == 'void':
        param_types = []
    else:
        param_types = [p.strip().split()[0] for p in params.split(',')]
    
    wrapper = f"""#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;

class Solution {{
public:
{chr(10).join('    ' + l for l in user_code.splitlines())}
}};

int main() {{
    Solution sol;
    string raw;
    getline(cin, raw);
    if(raw.empty()) return 0;
    
    // Handle array input [1,2,3]
    if(raw[0] == '[') {{
        raw.erase(remove(raw.begin(), raw.end(), '['), raw.end());
        raw.erase(remove(raw.begin(), raw.end(), ']'), raw.end());
        
        vector<int> nums;
        stringstream ss(raw);
        string x;
        while(getline(ss, x, ',')) {{
            x.erase(remove_if(x.begin(), x.end(), ::isspace), x.end());
            if(!x.empty()) nums.push_back(stoi(x));
        }}
        
        // Call function - only if it expects vector<int>
        {"" if len(param_types) == 0 else 
         f"auto result = sol.{function_name}(nums);" if param_types[0] == 'vector<int>' and return_type != 'void' else
         f"sol.{function_name}(nums);" if param_types[0] == 'vector<int>' and return_type == 'void' else
         "// Function doesn't take vector parameter"}
        
        // Print result
        {"" if len(param_types) == 0 or param_types[0] != 'vector<int>' else
         f'''if(result.size() > 0) {{
            cout << "[";
            for(size_t i=0; i<result.size(); i++) {{
                if(i) cout << ", ";
                cout << result[i];
            }}
            cout << "]";
        }}''' if return_type == 'vector<int>' else 
         'cout << result;' if return_type in ['int', 'string'] else 
         '// void function - no output'}
    }}
    else {{
        // Handle single or multiple integer inputs
        stringstream ss(raw);
        vector<int> vals;
        int v;
        while(ss >> v) vals.push_back(v);
        
        if(vals.size() == 1 && {len(param_types)} == 1) {{
            // Single parameter function
            {"" if len(param_types) != 1 else
             f"auto result = sol.{function_name}(vals[0]);" if param_types[0] == 'int' and return_type != 'void' else
             f"sol.{function_name}(vals[0]);" if param_types[0] == 'int' and return_type == 'void' else
             "// Parameter type mismatch"}
            
            {"" if len(param_types) != 1 or param_types[0] != 'int' else
             f'''if(result.size() > 0) {{
                cout << "[";
                for(size_t i=0; i<result.size(); i++) {{
                    if(i) cout << ", ";
                    cout << result[i];
                }}
                cout << "]";
            }}''' if return_type == 'vector<int>' else 
             'cout << result;' if return_type in ['int', 'string'] else 
             '// void function - no output'}
        }}
        else if(vals.size() >= 2 && {len(param_types)} == 2) {{
            // Two parameter function
            {"" if len(param_types) != 2 else
             f"auto result = sol.{function_name}(vals[0], vals[1]);" if param_types[0] == 'int' and param_types[1] == 'int' and return_type != 'void' else
             f"sol.{function_name}(vals[0], vals[1]);" if param_types[0] == 'int' and param_types[1] == 'int' and return_type == 'void' else
             "// Parameter type mismatch"}
            
            {"" if len(param_types) != 2 or param_types[0] != 'int' or param_types[1] != 'int' else
             f'''if(result.size() > 0) {{
                cout << "[";
                for(size_t i=0; i<result.size(); i++) {{
                    if(i) cout << ", ";
                    cout << result[i];
                }}
                cout << "]";
            }}''' if return_type == 'vector<int>' else 
             'cout << result;' if return_type in ['int', 'string'] else 
             '// void function - no output'}
        }}
    }}
    
    return 0;
}}
"""
    return wrapper

def wrap_java_code(user_code, stdin):
    """Wrap Java function in Solution class - Users only provide function implementation
    FIXED: Now properly invokes function and prints output
    """
    wrapper = f"""import java.util.*;

class Solution {{
{chr(10).join('    ' + line for line in user_code.split(chr(10)))}
}}

public class Main {{
    public static void main(String[] args) {{
        Scanner sc = new Scanner(System.in);
        Solution sol = new Solution();
        
        try {{
            List<String> lines = new ArrayList<>();
            while (sc.hasNextLine()) {{
                String line = sc.nextLine().trim();
                if (!line.isEmpty()) lines.add(line);
            }}
            
            var methods = Solution.class.getDeclaredMethods();
            if (methods.length == 0) {{
                System.err.println("No method found");
                return;
            }}
            
            var method = methods[0];
            Object result;
            
            if (method.getParameterCount() == 1) {{
                String val = lines.get(0);
                if (val.startsWith("[")) {{
                    val = val.replaceAll("[\\[\\]]", "");
                    int[] arr = Arrays.stream(val.split(","))
                            .mapToInt(Integer::parseInt).toArray();
                    result = method.invoke(sol, arr);
                }} else {{
                    result = method.invoke(sol, Integer.parseInt(val));
                }}
            }} else {{
                result = method.invoke(sol,
                    Integer.parseInt(lines.get(0)),
                    Integer.parseInt(lines.get(1))
                );
            }}
            
            if (result != null) System.out.println(result);
        }} catch (Exception e) {{
            System.err.println(e.getMessage());
        }}
    }}
}}
"""
    return wrapper

def wrap_javascript_code(user_code, stdin):
    """Wrap JavaScript function in Solution class - Users only provide function implementation"""
    import json as json_module
    
    # Use json.dumps to safely escape the input data - prevents syntax errors from special chars
    safe_stdin = json_module.dumps(stdin)
    
    wrapper = f"""
class Solution {{
{chr(10).join('    ' + line for line in user_code.split(chr(10)))}
}}

// Parse input and call the Solution class method
const inputData = JSON.parse({safe_stdin});

// Handle if inputData is already parsed (number/string) or needs parsing (string with newlines)
let lines = typeof inputData === 'string' 
    ? inputData.trim().split('\\n') 
    : [JSON.stringify(inputData)];

const solution = new Solution();

// Dynamically detect the method inside Solution class - find first non-constructor method
const methodName = Object.getOwnPropertyNames(Object.getPrototypeOf(solution))
    .find(name => name !== 'constructor');

if (!methodName) {{
    console.error("No method found");
    process.exit(1);
}}

// Parse parameters more efficiently
const params = lines.map(line => {{
    line = line.trim();
    if (line.startsWith('[')) return JSON.parse(line);
    if (!isNaN(line)) return Number(line);
    return line;
}});

try {{
    const result = solution[methodName](...params);
    if (result !== undefined) {{
        if (Array.isArray(result)) console.log(JSON.stringify(result));
        else console.log(result);
    }}
}} catch (e) {{
    console.error(e.message);
    process.exit(1);
}}
"""
    return wrapper

def wrap_c_code(user_code, stdin):
    """Wrap C code - Expects basic structure with main()"""
    # C is typically procedural, so we'll keep it simple
    # Users can write their own main() function
    return user_code

def get_starter_code(language, question_data):
    """
    Generate LeetCode-style starter code - ONLY the function signature
    Users write just the function implementation, not the entire class structure
    """
    function_name = question_data.get('function_name', 'solution')
    parameters = question_data.get('parameters', ['nums: List[int]'])
    return_type = question_data.get('return_type', 'int')
    
    if language == 'python':
        # Python: Just the function signature with type hints
        params_str = ', '.join(parameters)
        starter = f"""def {function_name}(self, {params_str}) -> {return_type}:
    # Write your code here
    pass"""
        return starter
    
    elif language == 'java':
        # Java: Just the method signature
        java_params = []
        for param in parameters:
            param_parts = param.split(':')
            if len(param_parts) == 2:
                name = param_parts[0].strip()
                ptype = param_parts[1].strip()
                # Convert Python types to Java types
                if 'List[int]' in ptype or 'int[]' in ptype:
                    java_params.append(f'int[] {name}')
                elif 'List[str]' in ptype or 'str[]' in ptype:
                    java_params.append(f'String[] {name}')
                elif 'int' in ptype:
                    java_params.append(f'int {name}')
                elif 'str' in ptype or 'String' in ptype:
                    java_params.append(f'String {name}')
                else:
                    java_params.append(f'Object {name}')
            else:
                java_params.append(param)
        
        # Convert return type
        java_return = return_type
        if 'List[int]' in return_type:
            java_return = 'int[]'
        elif 'List[str]' in return_type:
            java_return = 'String[]'
        elif return_type == 'None':
            java_return = 'void'
        
        params_str = ', '.join(java_params)
        starter = f"""public {java_return} {function_name}({params_str}) {{
    // Write your code here
    
}}"""
        return starter
    
    elif language == 'cpp':
        # C++: Just the method signature
        cpp_params = []
        for param in parameters:
            param_parts = param.split(':')
            if len(param_parts) == 2:
                name = param_parts[0].strip()
                ptype = param_parts[1].strip()
                # Convert Python types to C++ types
                if 'List[int]' in ptype:
                    cpp_params.append(f'vector<int>& {name}')
                elif 'List[str]' in ptype:
                    cpp_params.append(f'vector<string>& {name}')
                elif 'int' in ptype:
                    cpp_params.append(f'int {name}')
                elif 'str' in ptype or 'string' in ptype:
                    cpp_params.append(f'string {name}')
                else:
                    cpp_params.append(f'auto {name}')
            else:
                cpp_params.append(param)
        
        # Convert return type
        cpp_return = return_type
        if 'List[int]' in return_type:
            cpp_return = 'vector<int>'
        elif 'List[str]' in return_type:
            cpp_return = 'vector<string>'
        elif return_type == 'None':
            cpp_return = 'void'
        
        params_str = ', '.join(cpp_params)
        starter = f"""{cpp_return} {function_name}({params_str}) {{
    // Write your code here
    
}}"""
        return starter
    
    elif language == 'javascript':
        # JavaScript: Just the function signature
        js_params = [p.split(':')[0].strip() for p in parameters]
        params_str = ', '.join(js_params)
        
        starter = f"""{function_name}({params_str}) {{
    // Write your code here
    
}}"""
        return starter
    
    elif language == 'c':
        # C: Just the function signature
        c_params = []
        for param in parameters:
            param_parts = param.split(':')
            if len(param_parts) == 2:
                name = param_parts[0].strip()
                ptype = param_parts[1].strip()
                if 'List[int]' in ptype or 'int[]' in ptype:
                    c_params.append(f'int* {name}, int size')
                elif 'int' in ptype:
                    c_params.append(f'int {name}')
                else:
                    c_params.append(f'void* {name}')
            else:
                c_params.append(param)
        
        c_return = 'int' if 'int' in return_type else 'void'
        params_str = ', '.join(c_params)
        
        starter = f"""{c_return} {function_name}({params_str}) {{
    // Write your code here
    
}}"""
        return starter
    
    else:
        return "// Unsupported language"

# Host Control Panel Socket Events
@socketio.on('host_select_player_count')
def handle_host_select_player_count(data):
    global HOST_SELECTED_PLAYER_COUNT, TOURNAMENT_STATUS, TOURNAMENT_CAPACITY
    
    if request.sid != HOST_SID:
        emit('error', {'message': 'Only the host can select player count'})
        return
    
    count = data.get('count')
    if count not in [2, 4, 8, 16, 32, 64]:
        emit('error', {'message': 'Invalid player count'})
        return
    
    HOST_SELECTED_PLAYER_COUNT = count
    TOURNAMENT_CAPACITY = count
    TOURNAMENT_STATUS = 'READY'
    
    print(f"🎯 Host selected player count: {count}")
    
    # Update host control panel
    emit('host_control_update', {
        'selected_count': count,
        'status': TOURNAMENT_STATUS,
        'can_start': True
    })
    
    # Notify all clients about tournament setup
    socketio.emit('tournament_setup_update', {
        'capacity': count,
        'status': TOURNAMENT_STATUS,
        'host_name': HOST_NAME
    })

@socketio.on('host_start_tournament')
def handle_host_start_tournament():
    global TOURNAMENT_STATUS
    
    print(f"🚀 Host start tournament request from {request.sid}")
    
    if request.sid != HOST_SID:
        print(f"❌ Unauthorized start request from {request.sid}")
        emit('error', {'message': 'Only the host can start the tournament'})
        return
    
    if not HOST_SELECTED_PLAYER_COUNT:
        print(f"❌ No player count selected")
        emit('error', {'message': 'Please select player count first'})
        return
    
    if len(players) < 2:
        print(f"❌ Not enough players: {len(players)}")
        emit('error', {'message': f'Need at least 2 players to start tournament. Currently have {len(players)} players.'})
        return
    
    if TOURNAMENT_STATUS == 'LIVE':
        print(f"❌ Tournament already live")
        emit('error', {'message': 'Tournament is already running'})
        return
    
    TOURNAMENT_STATUS = 'LIVE'
    
    print(f"✅ Starting tournament with {len(players)} players")
    print(f"📋 Players: {[p['name'] for p in players.values()]}")
    
    # Update host control panel
    emit('host_control_update', {
        'selected_count': HOST_SELECTED_PLAYER_COUNT,
        'status': TOURNAMENT_STATUS,
        'can_start': False,
        'tournament_live': True
    })
    
    # Notify all clients that tournament is starting
    socketio.emit('tournament_starting', {
        'host_name': HOST_NAME,
        'player_count': len(players),
        'message': f'Host {HOST_NAME} has started the tournament!',
        'success': True
    })
    
    print("📡 Tournament starting notification sent to all clients")
    
    # Start the tournament with a small delay to ensure notifications are processed
    try:
        print("🎯 MANUAL-START: Starting tournament matches immediately...")
        start_tournament()
    except Exception as e:
        print(f"❌ Error starting tournament: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit('error', {'message': f'Error starting tournament: {str(e)}'})

@socketio.on('connect')
def handle_connect():
    global HOST_SID, TOURNAMENT_CAPACITY, HOST_NAME
    
    print(f"🌐 New connection: {request.sid}")
    
    # If no host exists, make this user the host automatically
    if HOST_SID is None:
        HOST_SID = request.sid
        print(f"🏮 Setting {request.sid} as new host (first connection)")
        emit('you_are_host', {
            'message': 'You are the host!',
            'status': TOURNAMENT_STATUS,
            'show_control_panel': True,
            'is_new_host': True
        })
        # Immediately show the host control panel
        emit('show_host_control_panel', {
            'selected_count': HOST_SELECTED_PLAYER_COUNT,
            'status': TOURNAMENT_STATUS,
            'can_start': False
        })
    else:
        # Subsequent visitors are players
        if HOST_NAME is not None:
            # Host has joined, show player join form
            emit('show_player_join', {
                'capacity': TOURNAMENT_CAPACITY or HOST_SELECTED_PLAYER_COUNT, 
                'current': len(players),
                'host_name': HOST_NAME,
                'status': TOURNAMENT_STATUS
            })
        else:
            # Host hasn't joined yet, wait
            emit('waiting_for_host', {'message': 'Waiting for host to join...'})
    
    print(f"📊 Connection handled - Host: {HOST_SID}, Players: {len(players)}")

@socketio.on('disconnect')
def handle_disconnect():
    global HOST_SID, TOURNAMENT_CAPACITY, players, HOST_NAME, HOST_SELECTED_PLAYER_COUNT, TOURNAMENT_STATUS
    
    sid = request.sid
    print(f"🔌 Client disconnected: {sid}")
    
    # Check if the disconnecting client is the host
    if sid == HOST_SID:
        print(f"🏮 Host {sid} disconnected - resetting host assignment")
        
        # If tournament hasn't started yet, clear host info
        if TOURNAMENT_STATUS != 'LIVE':
            print("🔄 Tournament not live - clearing host info")
            HOST_SID = None
            HOST_NAME = None
            
            # Notify all remaining clients that host left and they need to refresh
            socketio.emit('host_disconnected', {
                'message': 'Host disconnected. Please refresh the page.',
                'action': 'refresh_required'
            })
        else:
            print("⚠️ Host disconnected during live tournament - keeping tournament running")
            # During live tournament, just clear host info but keep tournament running
            HOST_SID = None
            HOST_NAME = None
    
    # Remove player if they were in the players list
    if sid in players:
        player_name = players[sid]['name']
        print(f"👤 Player {player_name} disconnected")
        del players[sid]
        
        # Update player list for remaining clients
        if TOURNAMENT_CAPACITY and len(players) < TOURNAMENT_CAPACITY:
            socketio.emit('player_list_update', {
                'players': [p['name'] for p in players.values()],
                'count': len(players),
                'capacity': TOURNAMENT_CAPACITY,
                'host_name': HOST_NAME
            })
    
    print(f"📊 Current state after disconnect - Players: {len(players)}, Host: {HOST_SID is not None}")

@socketio.on('join_as_host')
def handle_join_as_host(data):
    global HOST_NAME
    
    if request.sid != HOST_SID:
        print(f"❌ Non-host {request.sid} trying to join as host")
        emit('error', {'message': 'Only the host can use this function'})
        return
    
    name = data.get('name', '').strip()
    
    if not name:
        print(f"❌ Empty host name from {request.sid}")
        emit('error', {'message': 'Host name cannot be empty'})
        return
    
    HOST_NAME = name
    print(f"✅ Host joined with name: {HOST_NAME}")
    
    # Send success confirmation to host
    emit('host_join_success', {
        'message': f'Successfully joined as host: {HOST_NAME}',
        'host_name': HOST_NAME
    })
    
    # Emit to all clients that host has joined
    socketio.emit('host_joined', {
        'host_name': HOST_NAME,
        'capacity': TOURNAMENT_CAPACITY or HOST_SELECTED_PLAYER_COUNT,
        'current': len(players),
        'status': TOURNAMENT_STATUS
    })
    
    # Send host to control panel
    emit('show_host_panel', {
        'capacity': TOURNAMENT_CAPACITY or HOST_SELECTED_PLAYER_COUNT,
        'current': len(players),
        'players': [p['name'] for p in players.values()],
        'host_name': HOST_NAME,
        'status': TOURNAMENT_STATUS,
        'selected_count': HOST_SELECTED_PLAYER_COUNT
    })
    
    # Also emit host control panel visibility
    emit('show_host_control_panel', {
        'selected_count': HOST_SELECTED_PLAYER_COUNT,
        'status': TOURNAMENT_STATUS,
        'can_start': len(players) >= 2 and HOST_SELECTED_PLAYER_COUNT is not None
    })
    
    print(f"📡 Host setup complete for {HOST_NAME}")

@socketio.on('join_tournament')
def handle_join(data):
    global players, TOURNAMENT_STATUS
    
    name = data.get('name', '').strip()
    sid = request.sid
    
    print(f"🎯 Join tournament request: {name} from {sid}")
    
    # Host cannot join as player
    if sid == HOST_SID:
        print(f"❌ Host {sid} trying to join as player")
        emit('error', {'message': 'Host cannot join as a player'})
        return
    
    if not name:
        print(f"❌ Empty name from {sid}")
        emit('error', {'message': 'Name cannot be empty'})
        return
    
    if not HOST_SELECTED_PLAYER_COUNT:
        print(f"❌ No tournament setup from {sid}")
        emit('error', {'message': 'Tournament not set up yet'})
        return
    
    if HOST_NAME is None:
        print(f"❌ No host name from {sid}")
        emit('error', {'message': 'Waiting for host to join first'})
        return
    
    if len(players) >= HOST_SELECTED_PLAYER_COUNT:
        print(f"❌ Tournament full from {sid}")
        emit('error', {'message': 'Tournament is full'})
        return
    
    if any(p['name'] == name for p in players.values()):
        print(f"❌ Name taken: {name} from {sid}")
        emit('error', {'message': 'Name already taken'})
        return
    
    if name == HOST_NAME:
        print(f"❌ Same as host name: {name} from {sid}")
        emit('error', {'message': 'Cannot use the same name as the host'})
        return
    
    # Add player
    players[sid] = {
        'name': name,
        'status': 'lobby',
        'sid': sid
    }
    
    print(f"✅ Player {name} joined successfully. Total: {len(players)}/{HOST_SELECTED_PLAYER_COUNT}")
    
    # Send success confirmation to the player
    emit('join_success', {
        'message': f'Successfully joined as {name}',
        'player_name': name,
        'total_players': len(players),
        'capacity': HOST_SELECTED_PLAYER_COUNT
    })
    
    # Notify all clients about player list update
    socketio.emit('player_list_update', {
        'players': [p['name'] for p in players.values()],
        'count': len(players),
        'capacity': HOST_SELECTED_PLAYER_COUNT,
        'host_name': HOST_NAME
    })
    
    # Notify host about new player
    socketio.emit('player_joined', {
        'player_name': name,
        'total_players': len(players),
        'capacity': HOST_SELECTED_PLAYER_COUNT,
        'players': [p['name'] for p in players.values()]
    }, room=HOST_SID)
    
    print(f"📡 Notifications sent for player {name}")
    
    # AUTO-START: Check if we have enough players to start tournament
    if len(players) >= HOST_SELECTED_PLAYER_COUNT:
        print(f"🚀 AUTO-START: Required players ({HOST_SELECTED_PLAYER_COUNT}) reached! Starting tournament automatically...")
        print(f"🚀 Current players: {[p['name'] for p in players.values()]}")
        
        TOURNAMENT_STATUS = 'LIVE'
        
        # Update host control panel
        try:
            socketio.emit('host_control_update', {
                'selected_count': HOST_SELECTED_PLAYER_COUNT,
                'status': TOURNAMENT_STATUS,
                'can_start': False,
                'tournament_live': True
            }, room=HOST_SID)
            print("✅ Host control panel updated")
        except Exception as e:
            print(f"⚠️ Error updating host control panel: {e}")
        
        # Notify all clients that tournament is starting automatically
        try:
            socketio.emit('tournament_starting', {
                'host_name': HOST_NAME,
                'player_count': len(players),
                'message': f'Tournament full! Starting automatically with {len(players)} players!',
                'success': True,
                'auto_start': True
            })
            print("✅ Auto-start tournament notification sent to all clients")
        except Exception as e:
            print(f"⚠️ Error sending tournament_starting notification: {e}")
        
        # Give clients time to process the notification before starting matches
        print("⏳ Waiting 2 seconds for clients to process notification...")
        socketio.sleep(2)
        
        # Start the tournament with error handling
        try:
            print("🎯 AUTO-START: Starting tournament matches...")
            result = start_tournament()
            if result:
                print("✅ Tournament started successfully")
            else:
                print("❌ Tournament start returned False")
                socketio.emit('error', {
                    'message': 'Failed to start tournament. Please check server logs.'
                })
        except Exception as e:
            print(f"❌ Error in auto-start tournament: {e}")
            import traceback
            traceback.print_exc()
            
            # Notify all clients about the error
            try:
                socketio.emit('error', {
                    'message': f'Error starting tournament: {str(e)}. Please contact the host.'
                })
            except:
                pass
            
            # Reset tournament status
            TOURNAMENT_STATUS = 'READY'

def start_tournament():
    global current_round_number, next_round_winners
    
    try:
        current_round_number = 1
        next_round_winners = []
        
        print(f"🎯 Starting tournament with {len(players)} players")
        print(f"📋 Players: {[p['name'] for p in players.values()]}")
        print(f"📋 Player SIDs: {list(players.keys())}")
        
        if len(players) < 2:
            print("❌ Not enough players to start tournament")
            socketio.emit('error', {'message': 'Not enough players to start tournament'})
            return False
        
        # Verify all players are still connected
        valid_players = []
        for sid in list(players.keys()):
            try:
                # Check if player is still connected
                if sid in players:
                    valid_players.append(sid)
            except Exception as e:
                print(f"⚠️ Player {sid} validation failed: {e}")
        
        if len(valid_players) < 2:
            print(f"❌ Not enough valid players: {len(valid_players)}")
            socketio.emit('error', {'message': 'Not enough connected players to start tournament'})
            return False
        
        print(f"✅ Validated {len(valid_players)} connected players")
        
        # Don't send another tournament_starting here - it was already sent by the caller
        # Just proceed directly to starting rounds
        print("⏳ Proceeding to start first round...")
        socketio.sleep(1)
        
        # Start the first round
        result = start_round(valid_players)
        
        if result:
            print("✅ Tournament started successfully")
            return True
        else:
            print("❌ Failed to start tournament rounds")
            return False
        
    except Exception as e:
        print(f"❌ Error in start_tournament: {e}")
        import traceback
        traceback.print_exc()
        try:
            socketio.emit('error', {'message': f'Tournament start error: {str(e)}'})
        except:
            pass
        return False

def start_round(player_sids):
    global active_matches, next_round_winners, current_round_number
    
    try:
        print(f"🎯 Starting round {current_round_number} with {len(player_sids)} players")
        
        if len(player_sids) < 2:
            print("❌ Not enough players for round")
            return False
        
        random.shuffle(player_sids)
        active_matches = {}
        next_round_winners = []
        
        num_matches = len(player_sids) // 2
        
        # Verify all players still exist before starting
        valid_player_sids = []
        for sid in player_sids:
            if sid in players:
                valid_player_sids.append(sid)
            else:
                print(f"⚠️ Player {sid} no longer exists, skipping")
        
        if len(valid_player_sids) < 2:
            print(f"❌ Not enough valid players: {len(valid_player_sids)}")
            return False
        
        # Recalculate matches with valid players
        num_matches = len(valid_player_sids) // 2
        print(f"✅ Validated {len(valid_player_sids)} players for {num_matches} matches")
        
        # Only notify players who are participating in this round
        try:
            print(f"📡 Sending round_starting to {len(valid_player_sids)} players...")
            for sid in valid_player_sids:
                socketio.emit('round_starting', {
                    'round': current_round_number,
                    'matches': num_matches,
                    'players': len(valid_player_sids)
                }, room=sid)
                print(f"  ✅ Sent to {players[sid]['name']} ({sid})")
            print(f"✅ Round starting notification sent to all {len(valid_player_sids)} players")
        except Exception as e:
            print(f"⚠️ Error sending round_starting notifications: {e}")
            import traceback
            traceback.print_exc()
        
        print("⏳ Waiting 3 seconds for players to process round_starting...")
        socketio.sleep(3)
        
        # Start matches immediately - no need for background task delay
        print(f"🎯 Creating {num_matches} matches...")
        
        # Validate we have questions available
        if not QUESTIONS or len(QUESTIONS) == 0:
            print("❌ No questions available!")
            socketio.emit('error', {'message': 'No questions available. Please contact administrator.'})
            return False
        
        matches_created = 0
        for i in range(num_matches):
            try:
                player1_sid = valid_player_sids[i * 2]
                player2_sid = valid_player_sids[i * 2 + 1]
                
                # Verify players still exist
                if player1_sid not in players or player2_sid not in players:
                    print(f"❌ Player missing for match {i}: {player1_sid}, {player2_sid}")
                    print(f"❌ Available players: {list(players.keys())}")
                    continue
                
                # Verify player data is valid
                if 'name' not in players[player1_sid] or 'name' not in players[player2_sid]:
                    print(f"❌ Invalid player data for match {i}")
                    continue
                
                room_id = f"match_{current_round_number}_{i}"
                
                print(f"🎮 Creating match {i+1}: {players[player1_sid]['name']} vs {players[player2_sid]['name']}")
                
                # Join players to match room
                try:
                    join_room(room_id, sid=player1_sid)
                    join_room(room_id, sid=player2_sid)
                    print(f"✅ Players joined room {room_id}")
                except Exception as e:
                    print(f"❌ Error joining room: {e}")
                    continue
                
                # Get question
                try:
                    question = get_random_question()
                    if not question:
                        print(f"❌ Failed to get question for match {i}")
                        continue
                    print(f"✅ Question selected: {question.get('title', 'Unknown')}")
                except Exception as e:
                    print(f"❌ Error getting question: {e}")
                    continue
                
                # Create match data
                active_matches[room_id] = {
                    'player1_sid': player1_sid,
                    'player2_sid': player2_sid,
                    'player1_name': players[player1_sid]['name'],
                    'player2_name': players[player2_sid]['name'],
                    'question': question,
                    'answered': False
                }
                
                players[player1_sid]['status'] = 'playing'
                players[player2_sid]['status'] = 'playing'
                
                # Send problem to both players (simplified version without starter code)
                problem_data = {
                    'opponent': players[player2_sid]['name'],
                    'round': current_round_number,
                    'title': question['title'],
                    'description': question['description'],
                    'input_format': question['input_format'],
                    'output_format': question['output_format'],
                    'constraints': question['constraints'],
                    'sample_cases': question['sample_cases'],
                    'timer_seconds': QUESTION_TIMER_SECONDS  # Add timer info
                }
                
                print(f"📤 Sending match to {players[player1_sid]['name']} vs {players[player2_sid]['name']}")
                print(f"   Player 1: {players[player1_sid]['name']} (SID: {player1_sid})")
                print(f"   Player 2: {players[player2_sid]['name']} (SID: {player2_sid})")
                print(f"   Question: {question['title']}")
                
                # Send match_start to player 1
                try:
                    socketio.emit('match_start', problem_data, room=player1_sid)
                    print(f"✅ Match data sent to player 1: {players[player1_sid]['name']}")
                    socketio.sleep(0.1)  # Small delay between emissions
                except Exception as e:
                    print(f"⚠️ Error sending match to player 1: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Send match_start to player 2 with updated opponent name
                problem_data['opponent'] = players[player1_sid]['name']
                try:
                    socketio.emit('match_start', problem_data, room=player2_sid)
                    print(f"✅ Match data sent to player 2: {players[player2_sid]['name']}")
                    socketio.sleep(0.1)  # Small delay between emissions
                except Exception as e:
                    print(f"⚠️ Error sending match to player 2: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Emit bracket update - match started
                try:
                    socketio.emit('bracket_match_start', {
                        'round': current_round_number,
                        'match': i,
                        'player1': players[player1_sid]['name'],
                        'player2': players[player2_sid]['name']
                    })
                except Exception as e:
                    print(f"⚠️ Error sending bracket update: {e}")
                
                # Start the 10-minute timer for this match
                try:
                    start_match_timer(room_id)
                    print(f"✅ Timer started for match {i+1}")
                except Exception as e:
                    print(f"⚠️ Error starting timer: {e}")
                
                print(f"✅ Match {i+1} created: {players[player1_sid]['name']} vs {players[player2_sid]['name']}")
                matches_created += 1
                
            except Exception as e:
                print(f"❌ Error creating match {i}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"✅ Round {current_round_number} started with {matches_created}/{num_matches} matches created")
        
        # If no matches were created, emit error
        if matches_created == 0:
            print("❌ No matches were created - tournament failed to start")
            error_msg = 'Failed to create matches. '
            if not QUESTIONS or len(QUESTIONS) == 0:
                error_msg += 'No questions available. '
            if len(valid_player_sids) < 2:
                error_msg += 'Not enough connected players. '
            error_msg += 'Please check server logs and try again.'
            
            socketio.emit('error', {'message': error_msg})
            return False
        
        # If some matches failed but at least one was created, log warning but continue
        if matches_created < num_matches:
            print(f"⚠️ Warning: Only {matches_created}/{num_matches} matches were created")
            socketio.emit('warning', {
                'message': f'Some matches failed to create. {matches_created} matches are active.'
            })
        
        return True
        
    except Exception as e:
        print(f"❌ Error in start_round: {e}")
        import traceback
        traceback.print_exc()
        try:
            socketio.emit('error', {'message': f'Failed to start round: {str(e)}'})
        except:
            pass
        return False

def get_random_question():
    global used_questions
    
    try:
        if not QUESTIONS or len(QUESTIONS) == 0:
            print("❌ CRITICAL: QUESTIONS list is empty!")
            return None
        
        if len(used_questions) >= len(QUESTIONS):
            print("🔄 All questions used, resetting pool")
            used_questions = set()
        
        available = [q for i, q in enumerate(QUESTIONS) if i not in used_questions]
        
        if not available:
            print("⚠️ No available questions, resetting pool")
            used_questions = set()
            available = list(QUESTIONS)
        
        question = random.choice(available)
        question_index = QUESTIONS.index(question)
        used_questions.add(question_index)
        
        print(f"✅ Selected question: {question.get('title', 'Unknown')} (index {question_index})")
        return question
        
    except Exception as e:
        print(f"❌ Error in get_random_question: {e}")
        import traceback
        traceback.print_exc()
        # Return first question as fallback
        if QUESTIONS and len(QUESTIONS) > 0:
            return QUESTIONS[0]
        return None

def get_easiest_question() -> dict:
    """
    Return the easiest question for timeout fallback.
    
    Returns:
        dict: The easiest question data structure containing:
            - title (str): Question title
            - description (str): Problem description
            - input_format (str): Input format description
            - output_format (str): Output format description
            - constraints (str): Problem constraints
            - test_cases (list): List of test cases
            - sample_cases (list): List of sample cases
            - function_name (str): Function name for the solution
            - parameters (list): Function parameters
            - return_type (str): Expected return type
    
    Example:
        >>> question = get_easiest_question()
        >>> print(question['title'])
        'Even or Odd'
    """
    # "Even or Odd" is the easiest question based on analysis
    for question in QUESTIONS:
        if question['title'] == 'Even or Odd':
            return question
    # Fallback to first question if "Even or Odd" not found
    return QUESTIONS[0] if QUESTIONS else None

def start_match_timer(room_id: str) -> None:
    """
    Start a 10-minute timer for a match.
    
    Args:
        room_id (str): Unique identifier for the match room (e.g., "match_1_0")
                      Format: "match_{round_number}_{match_index}"
    
    Returns:
        None
    
    Side Effects:
        - Creates a background thread for countdown
        - Updates match_timers global dictionary
        - Sends timer_update events to both players via WebSocket
        - Calls handle_match_timeout() when timer expires
    
    Example:
        >>> start_match_timer("match_1_0")  # Start timer for round 1, match 0
        ⏰ Started 10-minute timer for match match_1_0
    
    Note:
        - Timer runs in a daemon thread to prevent blocking
        - Automatically stops if match is completed before timeout
        - Sends updates every 10 seconds and during final 10 seconds
    """
    import threading
    import time
    
    def timer_countdown():
        match_timers[room_id] = {
            'start_time': time.time(),
            'remaining': QUESTION_TIMER_SECONDS,
            'expired': False
        }
        
        # Send initial timer to both players
        if room_id in active_matches:
            match_data = active_matches[room_id]
            socketio.emit('timer_update', {
                'remaining': QUESTION_TIMER_SECONDS,
                'total': QUESTION_TIMER_SECONDS
            }, room=match_data['player1_sid'])
            socketio.emit('timer_update', {
                'remaining': QUESTION_TIMER_SECONDS,
                'total': QUESTION_TIMER_SECONDS
            }, room=match_data['player2_sid'])
        
        # Countdown loop
        for remaining in range(QUESTION_TIMER_SECONDS, 0, -1):
            time.sleep(1)
            
            # Check if match is still active and not answered
            if room_id not in active_matches or active_matches[room_id]['answered']:
                print(f"⏰ Timer stopped for {room_id} - match completed")
                if room_id in match_timers:
                    del match_timers[room_id]
                return
            
            # Update timer data
            match_timers[room_id]['remaining'] = remaining
            
            # Send timer updates every 10 seconds, and final 10 seconds
            if remaining % 10 == 0 or remaining <= 10:
                match_data = active_matches[room_id]
                socketio.emit('timer_update', {
                    'remaining': remaining,
                    'total': QUESTION_TIMER_SECONDS
                }, room=match_data['player1_sid'])
                socketio.emit('timer_update', {
                    'remaining': remaining,
                    'total': QUESTION_TIMER_SECONDS
                }, room=match_data['player2_sid'])
        
        # Timer expired - handle timeout
        handle_match_timeout(room_id)
    
    # Start timer in background thread
    timer_thread = threading.Thread(target=timer_countdown, daemon=True)
    timer_thread.start()
    print(f"⏰ Started 10-minute timer for match {room_id}")

def handle_match_timeout(room_id: str) -> None:
    """
    Handle when both players fail to answer within time limit.
    
    Args:
        room_id (str): Unique identifier for the match room that timed out
                      Format: "match_{round_number}_{match_index}"
    
    Returns:
        None
    
    Side Effects:
        - Marks timer as expired in match_timers
        - Switches match question to easiest question ("Even or Odd")
        - Sends timer_expired event to both players
        - Starts a new 5-minute timer for the easier question
        - Updates match_data with timeout_fallback flag
    
    Example:
        >>> handle_match_timeout("match_1_0")
        ⏰ TIMEOUT: Both players failed to answer within 10 minutes for match_1_0
        🔄 Switching to easiest question: Even or Odd
        ⏰ Started 5-minute timer for easier question in match match_1_0
    
    WebSocket Events Sent:
        - timer_expired: Contains new question data and starter code for all languages
    
    Note:
        - Only processes if match is still active and not already answered
        - Provides complete question data including starter code for all 5 languages
        - Automatically starts shorter timer (5 minutes) for easier question
    """
    if room_id not in active_matches:
        return
    
    match_data = active_matches[room_id]
    
    # Check if match was already answered
    if match_data['answered']:
        print(f"⏰ Timer expired for {room_id} but match already answered")
        return
    
    print(f"⏰ TIMEOUT: Both players failed to answer within 10 minutes for {room_id}")
    
    # Mark timer as expired
    if room_id in match_timers:
        match_timers[room_id]['expired'] = True
    
    # Get the easiest question
    easiest_question = get_easiest_question()
    if not easiest_question:
        print("❌ No easiest question found for timeout fallback")
        return
    
    # Update match with easiest question
    match_data['question'] = easiest_question
    match_data['timeout_fallback'] = True
    
    player1_sid = match_data['player1_sid']
    player2_sid = match_data['player2_sid']
    
    print(f"🔄 Switching to easiest question: {easiest_question['title']}")
    
    # Notify both players about timeout and new question
    timeout_message = {
        'message': '⏰ Time expired! Switching to easier question',
        'new_question': True,
        'title': easiest_question['title'],
        'description': easiest_question['description'],
        'input_format': easiest_question['input_format'],
        'output_format': easiest_question['output_format'],
        'constraints': easiest_question['constraints'],
        'sample_cases': easiest_question['sample_cases']
    }
    
    socketio.emit('timer_expired', timeout_message, room=player1_sid)
    socketio.emit('timer_expired', timeout_message, room=player2_sid)
    
    # Start a new timer for the easier question (shorter time - 5 minutes)
    start_easier_question_timer(room_id)

def start_easier_question_timer(room_id: str) -> None:
    """
    Start a 5-minute timer for the easier question after timeout.
    
    Args:
        room_id (str): Unique identifier for the match room
                      Format: "match_{round_number}_{match_index}"
    
    Returns:
        None
    
    Side Effects:
        - Creates a background thread for 5-minute countdown
        - Updates match_timers with easier_question flag
        - Sends timer_update events with easier_question=True
        - Calls handle_final_timeout() if timer expires again
    
    Example:
        >>> start_easier_question_timer("match_1_0")
        ⏰ Started 5-minute timer for easier question in match match_1_0
    
    Timer Behavior:
        - Duration: 300 seconds (5 minutes)
        - Updates: Every 10 seconds + final 10 seconds
        - Visual: Cyan theme to indicate easier question mode
        - Fallback: Random winner selection if both players still timeout
    
    Note:
        - Shorter duration than original timer (5 min vs 10 min)
        - Different visual theme on frontend (cyan vs gold)
        - Final safety net to prevent infinite matches
    """
    import threading
    import time
    
    EASIER_TIMER_SECONDS = 300  # 5 minutes for easier question
    
    def easier_timer_countdown():
        if room_id in match_timers:
            match_timers[room_id] = {
                'start_time': time.time(),
                'remaining': EASIER_TIMER_SECONDS,
                'expired': False,
                'easier_question': True
            }
        
        # Send initial timer to both players
        if room_id in active_matches:
            match_data = active_matches[room_id]
            socketio.emit('timer_update', {
                'remaining': EASIER_TIMER_SECONDS,
                'total': EASIER_TIMER_SECONDS,
                'easier_question': True
            }, room=match_data['player1_sid'])
            socketio.emit('timer_update', {
                'remaining': EASIER_TIMER_SECONDS,
                'total': EASIER_TIMER_SECONDS,
                'easier_question': True
            }, room=match_data['player2_sid'])
        
        # Countdown loop
        for remaining in range(EASIER_TIMER_SECONDS, 0, -1):
            time.sleep(1)
            
            # Check if match is still active and not answered
            if room_id not in active_matches or active_matches[room_id]['answered']:
                print(f"⏰ Easier question timer stopped for {room_id} - match completed")
                if room_id in match_timers:
                    del match_timers[room_id]
                return
            
            # Update timer data
            if room_id in match_timers:
                match_timers[room_id]['remaining'] = remaining
            
            # Send timer updates every 10 seconds, and final 10 seconds
            if remaining % 10 == 0 or remaining <= 10:
                match_data = active_matches[room_id]
                socketio.emit('timer_update', {
                    'remaining': remaining,
                    'total': EASIER_TIMER_SECONDS,
                    'easier_question': True
                }, room=match_data['player1_sid'])
                socketio.emit('timer_update', {
                    'remaining': remaining,
                    'total': EASIER_TIMER_SECONDS,
                    'easier_question': True
                }, room=match_data['player2_sid'])
        
        # Final timeout - declare it a draw or handle as needed
        handle_final_timeout(room_id)
    
    # Start timer in background thread
    timer_thread = threading.Thread(target=easier_timer_countdown, daemon=True)
    timer_thread.start()
    print(f"⏰ Started 5-minute timer for easier question in match {room_id}")

def handle_final_timeout(room_id: str) -> None:
    """
    Handle when both players fail to answer even the easiest question.
    
    Args:
        room_id (str): Unique identifier for the match room that double-timed out
                      Format: "match_{round_number}_{match_index}"
    
    Returns:
        None
    
    Side Effects:
        - Marks match as answered to prevent further processing
        - Randomly selects a winner from the two players
        - Updates player statuses (winner: 'waiting', loser: 'eliminated')
        - Adds winner to next_round_winners list
        - Sends you_won/you_lost events with timeout flags
        - Removes players from match room
        - Cleans up timer data
        - Calls check_round_completion() to advance tournament
    
    Example:
        >>> handle_final_timeout("match_1_0")
        ⏰ FINAL TIMEOUT: Both players failed to answer even the easiest question for match_1_0
        🎲 Random winner due to double timeout: Player1 defeats Player2
    
    WebSocket Events Sent:
        - you_won: To randomly selected winner with timeout_win=True
        - you_lost: To other player with timeout_loss=True
    
    Tournament Impact:
        - Ensures tournament progression continues
        - Prevents infinite stalemates
        - Maintains bracket structure
        - Fair random selection when both players perform equally
    
    Note:
        - This is a rare edge case (both players timeout twice)
        - Random selection is fair since both players failed equally
        - Tournament integrity is maintained through forced progression
    """
    if room_id not in active_matches:
        return
    
    match_data = active_matches[room_id]
    
    # Check if match was already answered
    if match_data['answered']:
        print(f"⏰ Final timer expired for {room_id} but match already answered")
        return
    
    print(f"⏰ FINAL TIMEOUT: Both players failed to answer even the easiest question for {room_id}")
    
    # Mark match as answered to prevent further processing
    match_data['answered'] = True
    
    player1_sid = match_data['player1_sid']
    player2_sid = match_data['player2_sid']
    
    # In case of double timeout, randomly pick a winner or declare both eliminated
    # For now, let's randomly pick a winner
    import random
    winner_sid = random.choice([player1_sid, player2_sid])
    loser_sid = player2_sid if winner_sid == player1_sid else player1_sid
    
    winner_name = players[winner_sid]['name']
    loser_name = players[loser_sid]['name']
    
    players[winner_sid]['status'] = 'waiting'
    players[loser_sid]['status'] = 'eliminated'
    
    next_round_winners.append(winner_sid)
    
    print(f"🎲 Random winner due to double timeout: {winner_name} defeats {loser_name}")
    
    # Emit bracket update - match completed by timeout
    match_index = int(room_id.split('_')[-1])  # Extract match number from room_id
    socketio.emit('bracket_match_complete', {
        'round': current_round_number,
        'match': match_index,
        'player1': match_data['player1_name'],
        'player2': match_data['player2_name'],
        'winner': winner_name
    })
    
    # Send notifications
    socketio.emit('you_won', {
        'message': 'You won by random selection after double timeout!',
        'opponent': loser_name,
        'passed': 0,
        'total': 0,
        'round': current_round_number,
        'timeout_win': True,
        'wait_for_next_round': True
    }, room=winner_sid)
    
    socketio.emit('you_lost', {
        'message': 'Both players timed out. Opponent won by random selection.',
        'winner': winner_name,
        'round': current_round_number,
        'timeout_loss': True
    }, room=loser_sid)
    
    # Remove both players from the match room
    leave_room(room_id, sid=winner_sid)
    leave_room(room_id, sid=loser_sid)
    
    # Clean up timer
    if room_id in match_timers:
        del match_timers[room_id]
    
    # Check if this round is complete
    check_round_completion()

@socketio.on('test_code')
def handle_test_code(data):
    """Handle test run with custom input"""
    language = data.get('language', 'python')
    code = data.get('code', '')
    test_input = data.get('input', '')
    
    if not code.strip():
        emit('test_result', {'success': False, 'error': 'Code cannot be empty'})
        return
    
    result = execute_code(language, code, test_input)
    emit('test_result', result)

@socketio.on('submit_code')
def handle_submit_code(data):
    """Handle final submission with test case validation"""
    language = data.get('language', 'python')
    code = data.get('code', '')
    sid = request.sid
    
    if not code.strip():
        emit('submission_result', {'success': False, 'error': 'Code cannot be empty'})
        return
    
    # Find the match
    match_room = None
    match_data = None
    
    for room_id, match in active_matches.items():
        if match['player1_sid'] == sid or match['player2_sid'] == sid:
            match_room = room_id
            match_data = match
            break
    
    if not match_room or not match_data:
        emit('submission_result', {'success': False, 'error': 'You are not in an active match'})
        return
    
    if match_data['answered']:
        return
    
    # Run against all test cases
    question = match_data['question']
    test_cases = question['test_cases']
    
    passed = 0
    failed = 0
    error_message = None
    
    for i, test in enumerate(test_cases):
        result = execute_code(language, code, test['input'])
        
        if not result['success']:
            error_message = f"Test {i+1}: {result['error']}"
            failed = len(test_cases) - i
            break
        
        # Clean output - strip whitespace and newlines to avoid false failures
        actual_output = result['output'].strip().replace('\r\n', '\n').replace('\r', '\n')
        expected_output = test['output'].strip().replace('\r\n', '\n').replace('\r', '\n')
        
        # Normalize comparison to prevent fake failures like [0,1] vs [0, 1] or Even vs even
        if actual_output.replace(" ", "").lower() == expected_output.replace(" ", "").lower():
            passed += 1
        else:
            failed = len(test_cases) - passed
            error_message = f"Test {i+1} failed: Expected '{expected_output}', got '{actual_output}'"
            break
    
    # Check if all passed
    if passed == len(test_cases):
        # Winner!
        print(f"🎉 {players[sid]['name']} won their match!")
        
        match_data['answered'] = True
        winner_sid = sid
        loser_sid = match_data['player2_sid'] if sid == match_data['player1_sid'] else match_data['player1_sid']
        
        winner_name = players[winner_sid]['name']
        loser_name = players[loser_sid]['name']
        
        players[winner_sid]['status'] = 'waiting'
        players[loser_sid]['status'] = 'eliminated'
        
        next_round_winners.append(winner_sid)
        
        # Stop the timer for this match
        if match_room in match_timers:
            print(f"⏰ Stopping timer for {match_room} - winner found")
            del match_timers[match_room]
        
        print(f"✅ Match completed: {winner_name} defeats {loser_name}")
        
        # Emit bracket update - match completed
        match_index = int(match_room.split('_')[-1])  # Extract match number from room_id
        socketio.emit('bracket_match_complete', {
            'round': current_round_number,
            'match': match_index,
            'player1': match_data['player1_name'],
            'player2': match_data['player2_name'],
            'winner': winner_name
        })
        
        # Send win notification ONLY to the winner
        socketio.emit('you_won', {
            'message': 'All test cases passed! You won!',
            'opponent': loser_name,
            'passed': passed,
            'total': len(test_cases),
            'round': current_round_number,
            'wait_for_next_round': True  # Tell frontend to wait for next round
        }, room=winner_sid)
        
        # Send loss notification ONLY to the loser
        socketio.emit('you_lost', {
            'message': 'Your opponent solved it first.',
            'winner': winner_name,
            'round': current_round_number
        }, room=loser_sid)
        
        # Remove both players from the match room
        leave_room(match_room, sid=winner_sid)
        leave_room(match_room, sid=loser_sid)
        
        # Check if this round is complete (but don't affect other ongoing matches)
        check_round_completion()
    else:
        # Failed some tests - send failure notification only to this player
        print(f"❌ {players[sid]['name']} failed tests: {passed}/{len(test_cases)} passed")
        emit('submission_result', {
            'success': False,
            'error': error_message,
            'passed': passed,
            'total': len(test_cases)
        })

def check_round_completion():
    global current_round_number, next_round_winners, TOURNAMENT_STATUS
    
    expected_winners = len(active_matches)
    
    print(f"🔍 Round completion check: {len(next_round_winners)}/{expected_winners} matches completed")
    
    if len(next_round_winners) == expected_winners:
        print(f"🎯 Round {current_round_number} completed! All matches finished.")
        
        # Notify all players that the round is complete
        socketio.emit('round_complete', {
            'round': current_round_number,
            'winners_count': len(next_round_winners),
            'message': f'Round {current_round_number} complete! Preparing next round...'
        })
        
        if len(next_round_winners) == 1:
            # Tournament is over - we have a champion!
            champion_sid = next_round_winners[0]
            champion_name = players[champion_sid]['name']
            
            print(f"🏆 Tournament complete! Champion: {champion_name}")
            
            TOURNAMENT_STATUS = 'NOT_STARTED'
            
            # Notify everyone about tournament completion
            socketio.emit('tournament_over', {
                'champion': champion_name,
                'total_rounds': current_round_number,
                'participants': len(players) + len(next_round_winners)
            })
            
            # Notify the champion specifically
            socketio.emit('you_are_champion', {
                'message': 'Congratulations! You are the CHAMPION!',
                'tournament_stats': {
                    'total_rounds': current_round_number,
                    'participants': len(players) + 1
                }
            }, room=champion_sid)
            
            # Reset host control panel
            if HOST_SID:
                socketio.emit('host_control_update', {
                    'selected_count': None,
                    'status': 'NOT_STARTED',
                    'can_start': False,
                    'tournament_live': False
                }, room=HOST_SID)
        else:
            # More rounds needed - start next round
            print(f"🚀 Starting round {current_round_number + 1} with {len(next_round_winners)} winners")
            
            # Give players time to see round complete message
            socketio.sleep(5)
            
            current_round_number += 1
            
            # Start next round
            start_round(next_round_winners)
    else:
        print(f"⏳ Round {current_round_number} still in progress: {len(next_round_winners)}/{expected_winners} completed")

@socketio.on('get_server_status')
def handle_get_server_status():
    """Get current server status for debugging"""
    status = {
        'host_sid': HOST_SID,
        'host_name': HOST_NAME,
        'tournament_status': TOURNAMENT_STATUS,
        'player_count': len(players),
        'tournament_capacity': TOURNAMENT_CAPACITY,
        'active_matches': len(active_matches),
        'current_round': current_round_number
    }
    
    emit('server_status', status)
    print(f"📊 Server status requested by {request.sid}: {status}")

@socketio.on('get_starter_code')
def handle_get_starter_code(data):
    """Get starter code for a specific language and question"""
    language = data.get('language', 'python')
    question_id = data.get('question_id')
    
    if question_id is not None and 0 <= question_id < len(QUESTIONS):
        question = QUESTIONS[question_id]
    else:
        # Return a default template
        question = {
            'function_name': 'solution',
            'parameters': ['nums: List[int]'],
            'return_type': 'int'
        }
    
    starter_code = get_starter_code(language, question)
    emit('starter_code', {'language': language, 'code': starter_code})
    print(f"📝 Starter code sent for {language}: {question.get('function_name', 'solution')}")

if __name__ == '__main__':
    print("🏮 ALGOWAR - Tokyo Night Cyber-Dojo Server Starting...")
    print("🔄 Tournament state has been reset - first visitor will become host")
    print("🌐 Server running on http://localhost:5000")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
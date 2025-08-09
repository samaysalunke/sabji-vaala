#!/usr/bin/env python3
"""
Fix the MCP server by adding validate tool and updating protocol version
"""

import re

# Read the current file
with open('puch_mcp_server.py', 'r') as f:
    content = f.read()

# 1. Add validate tool to TOOLS array (before the closing bracket)
validate_tool = '''    },
    {
        "name": "validate",
        "description": "Validate bearer token and return server owner's phone number (required by Puch AI)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "description": "Bearer token to validate"
                }
            },
            "required": ["token"]
        }'''

# Insert validate tool before the last tool's closing brace
content = content.replace(
    '            "required": ["vegetable"]\n        }\n    }\n]',
    '            "required": ["vegetable"]\n        }' + validate_tool + '\n    }\n]'
)

# 2. Add validate tool implementation function
validate_implementation = '''
def execute_validate(token: str) -> str:
    """Validate bearer token and return phone number (required by Puch AI)"""
    
    if token == AUTH_TOKEN:
        # Return phone number in required format: {country_code}{number}
        return MY_NUMBER  # 919998881729
    else:
        return "Invalid token"
'''

# Insert after the last tool implementation
content = content.replace(
    'def execute_compare_vegetable_prices(vegetable: str) -> str:',
    validate_implementation + '\ndef execute_compare_vegetable_prices(vegetable: str) -> str:'
)

# 3. Add validate tool to MCP handler
validate_handler = '''            elif tool_name == "validate":
                token = arguments.get("token", "")
                result = execute_validate(token)
                
'''

# Insert before the unknown tool error
content = content.replace(
    '            else:\n                return JSONResponse(content={',
    validate_handler + '            else:\n                return JSONResponse(content={'
)

# 4. Update protocol version from 2024-11-05 to 2025-06-18
content = content.replace(
    '"protocolVersion": "2024-11-05"',
    '"protocolVersion": "2025-06-18"'
)

# Write the updated file
with open('puch_mcp_server.py', 'w') as f:
    f.write(content)

print("✅ Added validate tool to TOOLS array")
print("✅ Added execute_validate() function")
print("✅ Added validate tool handler to MCP endpoint")
print("✅ Updated protocol version to 2025-06-18")
print("🎯 MCP server should now work with Puch AI!")

from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory store for flows (for simplicity).
# In production, you might use a database.
flows_storage = {}

@app.route('/')
def index():
    """Serve the front-end page."""
    return app.send_static_file('index.html')

@app.route('/save_flow', methods=['POST'])
def save_flow():
    """
    Endpoint to save flowchart JSON.
    Body must contain: { "flowId": "string", "flowData": {...} }
    """
    data = request.get_json()
    flow_id = data['flowId']
    flow_data = data['flowData']
    
    flows_storage[flow_id] = flow_data
    
    return jsonify({'message': 'Flow saved successfully!', 'flowId': flow_id}), 200

@app.route('/generate_code/<flow_id>', methods=['GET'])
def generate_code(flow_id):
    """
    Endpoint to generate code from a saved flow.
    Returns code as plain text (or you can render a template).
    """
    if flow_id not in flows_storage:
        return jsonify({'error': f'No flow found with ID {flow_id}'}), 404
    
    flow_data = flows_storage[flow_id]
    
    # Here’s a trivial example of code generation:
    # We’ll pretend that each node is an API call that just prints something.
    generated = generate_python_code(flow_data)
    
    # Option A: Return raw code in JSON
    # return jsonify({'code': generated})
    
    # Option B: Render an HTML template that displays the code
    return render_template('generated_code.html', code=generated)


def generate_python_code(flow_data):
    """
    Very simplistic "code generator" that loops through nodes and connections.
    Customize as needed for your real logic.
    """
    nodes = flow_data.get('nodes', [])
    edges = flow_data.get('edges', [])
    
    code_lines = [
        "import requests",
        "",
        "def run_flow():",
        "    print('Starting flow...')"
    ]
    
    for node in nodes:
        if node['type'] == 'APICall':
            endpoint = node.get('endpoint', '/')
            method = node.get('method', 'GET').upper()
            code_lines.append(f"    # Node {node['id']}: APICall to {endpoint} ({method})")
            code_lines.append(f"    response_{node['id']} = requests.{method.lower()}('http://example.com{endpoint}')")
            code_lines.append(f"    print('Response from node {node['id']}:', response_{node['id']}.status_code)")
        
        elif node['type'] == 'Decision':
            condition = node.get('condition', 'True')
            code_lines.append(f"    # Node {node['id']}: Decision with condition: {condition}")
            code_lines.append(f"    if {condition}:")
            code_lines.append(f"        print('Decision node {node['id']}: condition met')")
            code_lines.append(f"    else:")
            code_lines.append(f"        print('Decision node {node['id']}: condition not met')")
        
        # Add more node types as needed
    
    code_lines.append("    print('Flow complete!')")
    
    return "\n".join(code_lines)

if __name__ == '__main__':
    # For local development
    app.run(debug=True)

# OBS01PY Node Development Template

This template provides everything you need to develop a new node for the OBS01PY system. It's designed to reduce development overhead and ensure consistency across all nodes.

## 🚀 Quick Start

1. **Copy this template:**
```bash
cp -r template-node/ my-new-node/
cd my-new-node/
```

2. **Rename the node:**
```bash
# Update node name in config.json
# Update class name in template_node.py
# Update README.md
```

3. **Implement your functionality:**
```bash
# Add your specific logic to template_node.py
# Add tests to tests/
# Update documentation in docs/
```

4. **Test your node:**
```bash
python src/template_node/template_node.py
```

## 🎯 What You Get Out of the Box

### **BaseNode Integration**
- ✅ **Inherits all IPC communication capabilities** from BaseNode
- ✅ **Standardized message handling** for COMMAND, RESPONSE, STATUS, EMERGENCY, HEARTBEAT, DATA
- ✅ **Priority system** with LOW, NORMAL, HIGH, CRITICAL, EMERGENCY levels
- ✅ **Direct node communication** for emergency scenarios
- ✅ **Automatic heartbeat** and health monitoring
- ✅ **Message acknowledgment** and timeout handling
- ✅ **Error handling** and logging infrastructure
- ✅ **Built-in database querying** via DB Client node with FILTER, SORT, and async callbacks

### **Configuration Management**
- ✅ **JSON-based configuration** with validation
- ✅ **Environment-specific configs** (dev, test, prod)
- ✅ **Default values** and configuration inheritance
- ✅ **Runtime configuration updates**

### **Database Integration**
- ✅ **Query database via IPC** using `node.query_db()` method
- ✅ **Filter and sort results** with MongoDB-style queries
- ✅ **Async response handling** with callbacks
- ✅ **Real-time data streaming** - query continuously for latest values (e.g., heading, position)
- ✅ **No direct DB connection needed** - all queries go through DB Client node
- ✅ **See complete camera node example** below (Section 4) for heading queries

**Quick Example:**
```python
# Get latest heading value (for camera pointing north)
node.query_db(
    collection="Navigation",
    query_filter={"title": "heading"},
    sort=[("timestamp", -1)],  # Most recent first
    limit=1,
    callback=lambda msg, addr: print(f"Heading: {msg.payload['query_results'][0]['heading']}")
)
```

### **Testing Framework**
- ✅ **Unit test templates** with pytest
- ✅ **Integration test examples**
- ✅ **Mock objects** for testing IPC communication
- ✅ **Test data fixtures** and utilities

### **Documentation**
- ✅ **Complete API documentation**
- ✅ **Usage examples** and patterns
- ✅ **Troubleshooting guide**
- ✅ **Best practices** and conventions

## 📁 Template Structure

```
template-node/
├── src/template_node/          # Node implementation
│   ├── template_node.py        # Main node class
│   └── __init__.py
├── tests/                      # Test files
│   ├── test_template_node.py   # Unit tests
│   └── test_integration.py     # Integration tests
├── docs/                       # Documentation
│   ├── api.md                 # API documentation
│   └── examples.md             # Usage examples
├── examples/                   # Example implementations
│   ├── simple_node.py          # Simple node example
│   └── advanced_node.py       # Advanced node example
├── config.json                 # Node configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🔧 Node Development Guide

### 1. Basic Node Structure

```python
from base_node import BaseNode, MessageType, Priority

class MyNode(BaseNode):
    def __init__(self, config):
        super().__init__("my_node", config)
        
        # Add your node-specific initialization
        self.my_data = {}
        
        # Register custom message handlers
        self.register_handler("my_command", self._handle_my_command)
    
    def _handle_my_command(self, message, addr):
        """Handle custom commands"""
        # Your command logic here
        pass
```

### 2. Configuration

Edit `config.json`:

```json
{
    "node_name": "my_node",
    "node_port": 14560,
    "master_core_host": "localhost",
    "master_core_port": 14551,
    "direct_communication": true,
    "emergency_nodes": ["can_controller"],
    
    "my_specific_setting": "value",
    "my_timeout": 30
}
```

### 3. Message Handling

```python
def _handle_custom_message(self, message, addr):
    """Handle custom messages"""
    command = message.payload.get("command")
    
    if command == "do_something":
        result = self._do_something()
        
        # Send response
        response = NodeMessage(
            message_id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            priority=Priority.NORMAL,
            source=self.node_name,
            destination=message.source,
            payload={"result": result},
            timestamp=time.time()
        )
        self._send_message(response, addr)
```

### 4. Database Querying

BaseNode provides built-in support for querying the database via the DB Client node:

```python
# Simple query
node.query_db(
    collection="System",
    limit=10
)

# Query with filter
node.query_db(
    collection="System",
    query_filter={"status": "ONLINE"},
    limit=10
)

# Query with sort
node.query_db(
    collection="System",
    query_filter={"name": "Arrow 600 MVP"},
    sort=[("startuptime", -1)],  # Sort by startuptime descending
    limit=10
)

# Query with callback (async response handling)
def handle_query_response(message, addr):
    if message.payload.get("status") == "success":
        results = message.payload.get("query_results", [])
        print(f"Received {len(results)} documents")
        for doc in results:
            print(f"  - {doc.get('name', 'Unknown')}")

node.query_db(
    collection="System",
    query_filter={"status": "ONLINE"},
    callback=handle_query_response
)
```

**Note:** Ensure your node config includes the DB client in `known_nodes`:
```json
{
    "known_nodes": {
        "db_client": {
            "host": "localhost",
            "port": 14552
        }
    }
}
```

#### Real-World Example: Camera Node Querying Heading Values

Here's a complete example of a camera node that needs to query heading values to point north:

```python
from base_node import BaseNode, MessageType, Priority, NodeMessage
import time

class CameraNode(BaseNode):
    def __init__(self, config):
        super().__init__("camera_node", config)
        self.current_heading = None
        self.heading_update_interval = 1.0  # Query every second
        
    def start(self):
        super().start()
        # Register handler for DB query responses
        self.register_handler("response", self._handle_db_response)
        
        # Start periodic heading queries
        self._start_heading_monitor()
    
    def _handle_db_response(self, message: NodeMessage, addr: tuple):
        """Handle response from DB client"""
        payload = message.payload
        if payload.get("status") == "success":
            results = payload.get("query_results", [])
            if results:
                # Get the most recent heading value
                latest_heading = results[0]
                self.current_heading = latest_heading.get("heading", 0)
                self._adjust_camera_orientation()
    
    def _start_heading_monitor(self):
        """Continuously query latest heading value"""
        import threading
        
        def monitor_loop():
            while self.running:
                # Query latest heading from Navigation collection
                self.query_db(
                    collection="Navigation",
                    query_filter={"title": "heading"},  # Filter for heading messages
                    sort=[("timestamp", -1)],  # Most recent first
                    limit=1,  # Only need the latest
                    callback=self._handle_db_response
                )
                time.sleep(self.heading_update_interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def _adjust_camera_orientation(self):
        """Adjust camera to point north based on current heading"""
        if self.current_heading is not None:
            # Calculate adjustment needed (heading is typically 0-360 degrees)
            # North is typically 0 or 360, so adjust accordingly
            adjustment = -self.current_heading
            print(f"Adjusting camera by {adjustment}° to point north")
            # Your camera control logic here
            # e.g., self.camera.pan(adjustment)
    
    def get_current_heading(self):
        """Get the most recent heading value (one-time query)"""
        def callback(message, addr):
            payload = message.payload
            if payload.get("status") == "success":
                results = payload.get("query_results", [])
                if results:
                    return results[0].get("heading")
        
        self.query_db(
            collection="Navigation",
            query_filter={"title": "heading"},
            sort=[("timestamp", -1)],
            limit=1,
            callback=callback
        )
```

**Key Points:**
- Use `query_db()` for simple one-time queries or with callbacks for async responses
- Filter by `title` field to find specific message types (e.g., "heading", "latitude-longitude")
- Use `sort=[("timestamp", -1)]` to get the most recent data first
- Set `limit=1` when you only need the latest value
- Register a response handler to process async query results
- Use threading for continuous monitoring/streaming scenarios

### 5. Direct Node Communication

You can send messages directly to other nodes:

```python
self.send_to_node("can_controller", MessageType.COMMAND, {
    "command": "subscribe_data",
    "subscriber": self.node_name
})

# Send emergency message
self.send_emergency(["engine", "steering"], {
    "type": "emergency_stop",
    "reason": "sensor_failure"
})
```

### 6. Status Reporting

```python
def get_my_status(self):
    """Get node-specific status"""
    base_status = self.get_status()
    base_status.update({
        "my_data_count": len(self.my_data),
        "my_health": "good"
    })
    return base_status
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from template_node import TemplateNode

def test_node_initialization():
    config = {"node_port": 14560}
    node = TemplateNode(config)
    assert node.node_name == "template_node"
    assert node.status == "INITIALIZING"
```

### Integration Tests

```python
def test_node_communication():
    # Test communication with other nodes
    pass
```

Run tests:
```bash
pytest tests/ -v
```

## 📚 Examples

### Simple Node Example

See `examples/simple_node.py` for a basic implementation.

### Advanced Node Example

See `examples/advanced_node.py` for a more complex implementation with:
- Custom message handlers
- Background tasks
- Error handling
- Status reporting

## 🔄 Integration with OBS01PY

### 1. Add to Master Core

Update the master core configuration to include your node:

```json
{
    "nodes": {
        "my_node": {
            "type": "my_node",
            "port": 14560,
            "script_path": "nodes/my-node/src/my_node/my_node.py"
        }
    }
}
```

### 2. Update Submodule

```bash
# In main OBS01PY directory
git submodule add https://github.com/FrostUnmanned-Development/my-node.git nodes/my-node
```

### 3. Test Integration

```bash
# Start master core
python src/onboard_core/obs_core_node.py

# Start your node
python src/onboard_core/obs_client.py start_node my_node

# Check status
python src/onboard_core/obs_client.py status
```

## 📋 Best Practices

### 1. Error Handling
- Always wrap external operations in try-catch blocks
- Log errors with appropriate levels
- Send error responses to requesting nodes

### 2. Resource Management
- Clean up resources in the `stop()` method
- Use context managers where possible
- Handle connection failures gracefully

### 3. Message Design
- Use clear, descriptive command names
- Include all necessary data in payloads
- Set appropriate priority levels

### 4. Configuration
- Provide sensible defaults
- Document all configuration options
- Validate configuration on startup

### 5. Testing
- Write unit tests for all public methods
- Test error conditions
- Include integration tests

## 🚨 Emergency Procedures

### Emergency Stop
```python
def _handle_emergency_stop(self, message, addr):
    """Handle emergency stop"""
    logger.critical(f"EMERGENCY STOP from {message.source}")
    
    # Stop all operations
    self._stop_all_operations()
    
    # Notify other nodes
    self.send_emergency(self.emergency_nodes, {
        "type": "emergency_stop",
        "source": message.source
    })
```

### Health Monitoring
```python
def health_check(self):
    """Perform health check"""
    try:
        # Check critical components
        if not self._check_critical_components():
            return False
        
        # Send heartbeat
        self.send_heartbeat()
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

## 💡 Development Tips

### 1. Start Simple
- Begin with basic functionality
- Add complexity gradually
- Test each feature before moving on

### 2. Use the BaseNode Features
- Leverage built-in message handling
- Use the priority system appropriately
- Implement proper error handling

### 3. Follow the Patterns
- Study existing nodes (CAN Controller, DB Client)
- Use consistent naming conventions
- Follow the established architecture

### 4. Test Early and Often
- Write tests as you develop
- Test integration with other nodes
- Use the testing framework provided

### 5. Document Everything
- Comment your code
- Update documentation as you develop
- Include usage examples

## 📖 Documentation

- [API Documentation](docs/api.md) - Complete API reference
- [Examples](docs/examples.md) - Usage examples and patterns
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

1. Fork the template
2. Create your node implementation
3. Add tests and documentation
4. Submit a pull request

## 📄 License

This template is licensed under the Apache-2.0 License.
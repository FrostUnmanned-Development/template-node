# OBS01PY Node Development Template

This template provides everything you need to develop a new node for the OBS01PY system.

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
    "master_core_port": 14550,
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
            id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            priority=Priority.NORMAL,
            source=self.node_name,
            destination=message.source,
            payload={"result": result},
            timestamp=time.time()
        )
        self._send_message(response, addr)
```

### 4. Direct Communication

```python
# Send message to another node
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

### 5. Status Reporting

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
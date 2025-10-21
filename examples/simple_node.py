#!/usr/bin/env python3
"""
Simple Node Example - Minimal implementation of a BaseNode
This shows the simplest way to create a new node
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any
import json
import sys

# Add parent directory to path for base_node import
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src" / "onboard_core"))

from base_node import BaseNode, MessageType, Priority, NodeMessage
import uuid

logger = logging.getLogger(__name__)

class SimpleNode(BaseNode):
    """
    Simple Node - Minimal example showing basic node functionality
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("simple_node", config)
        
        # Simple counter
        self.counter = 0
        
        # Register one simple handler
        self.register_handler("increment", self._handle_increment)
        
        logger.info("Simple Node initialized")
    
    def _handle_increment(self, message: NodeMessage, addr: tuple):
        """Handle increment command"""
        self.counter += 1
        
        # Send response
        response = NodeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            priority=Priority.NORMAL,
            source=self.node_name,
            destination=message.source,
            payload={"counter": self.counter},
            timestamp=time.time()
        )
        self._send_message(response, addr)
        
        logger.info(f"Counter incremented to {self.counter}")

def main():
    """Main entry point"""
    config = {
        "node_port": 14561,
        "master_core_host": "localhost",
        "master_core_port": 14550
    }
    
    logging.basicConfig(level=logging.INFO)
    
    node = SimpleNode(config)
    if node.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    node.stop()

if __name__ == "__main__":
    main()

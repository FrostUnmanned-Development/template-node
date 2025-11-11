#!/usr/bin/env python3
"""
Template Node - Example implementation of a BaseNode
This serves as a template for developing new nodes in the OBS01PY system
"""

import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
import json
import os
import sys
import uuid
import platform
import tempfile
import argparse
import signal

# Import BaseNode from same package (with fallback for direct execution)
try:
    from .base_node import BaseNode, MessageType, Priority, NodeMessage
except ImportError:
    # Fallback for direct execution (not as package)
    # sys is already imported at top of file
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from template_node.base_node import BaseNode, MessageType, Priority, NodeMessage

logger = logging.getLogger(__name__)

class TemplateNode(BaseNode):
    """
    Template Node - Example implementation showing how to create a new node
    
    This node demonstrates:
    - Basic node initialization
    - Custom message handling
    - Background tasks
    - Status reporting
    - Error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("template_node", config)
        
        # Node-specific configuration
        self.my_timeout = config.get("my_timeout", 30)
        self.my_data = {}
        self.background_task_running = False
        self.background_thread = None
        
        # Register custom message handlers
        self.register_handler("template_command", self._handle_template_command)
        self.register_handler("get_data", self._handle_get_data)
        self.register_handler("set_data", self._handle_set_data)
        
        logger.info(f"Template Node initialized with timeout: {self.my_timeout}")
    
    def start(self):
        """Start the template node"""
        if not super().start():
            return False
        
        # Start background task
        self._start_background_task()
        
        self.status = "RUNNING"
        logger.info("Template Node started successfully")
        return True
    
    def stop(self):
        """Stop the template node"""
        self._stop_background_task()
        super().stop()
    
    def _start_background_task(self):
        """Start background processing task"""
        self.background_task_running = True
        self.background_thread = threading.Thread(target=self._background_worker)
        self.background_thread.daemon = True
        self.background_thread.start()
        logger.info("Background task started")
    
    def _stop_background_task(self):
        """Stop background processing task"""
        self.background_task_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        logger.info("Background task stopped")
    
    def _background_worker(self):
        """Background worker thread"""
        while self.background_task_running:
            try:
                # Perform background work
                self._do_background_work()
                time.sleep(1)  # Adjust timing as needed
            except Exception as e:
                logger.error(f"Error in background worker: {e}")
    
    def _do_background_work(self):
        """Perform background work"""
        # Example: Update internal data
        current_time = time.time()
        self.my_data["last_update"] = current_time
        self.my_data["uptime"] = current_time - self.last_heartbeat
        
        # Example: Send periodic status to master core
        if int(current_time) % 10 == 0:  # Every 10 seconds
            self.send_to_master_core(
                MessageType.STATUS,
                {"background_status": "running", "data_count": len(self.my_data)},
                Priority.LOW
            )
    
    def _handle_template_command(self, message: NodeMessage, addr: tuple):
        """Handle template-specific commands"""
        command = message.payload.get("command")
        
        try:
            if command == "start_processing":
                self._start_processing()
                response_data = {"status": "processing_started"}
            elif command == "stop_processing":
                self._stop_processing()
                response_data = {"status": "processing_stopped"}
            elif command == "reset":
                self._reset_node()
                response_data = {"status": "node_reset"}
            else:
                response_data = {"error": f"Unknown command: {command}"}
            
            # Send response
            self._send_response(message, response_data, addr)
            
        except Exception as e:
            logger.error(f"Error handling template command: {e}")
            self._send_error_response(message, str(e), addr)
    
    def _handle_get_data(self, message: NodeMessage, addr: tuple):
        """Handle data retrieval requests"""
        try:
            key = message.payload.get("key")
            
            if key:
                # Get specific data
                data = self.my_data.get(key, None)
                response_data = {"key": key, "value": data}
            else:
                # Get all data
                response_data = {"data": self.my_data}
            
            self._send_response(message, response_data, addr)
            
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            self._send_error_response(message, str(e), addr)
    
    def _handle_set_data(self, message: NodeMessage, addr: tuple):
        """Handle data setting requests"""
        try:
            key = message.payload.get("key")
            value = message.payload.get("value")
            
            if key is not None and value is not None:
                self.my_data[key] = value
                response_data = {"status": "data_set", "key": key, "value": value}
            else:
                response_data = {"error": "Missing key or value"}
            
            self._send_response(message, response_data, addr)
            
        except Exception as e:
            logger.error(f"Error setting data: {e}")
            self._send_error_response(message, str(e), addr)
    
    def _start_processing(self):
        """Start processing (example method)"""
        logger.info("Starting processing...")
        # Add your processing logic here
        self.my_data["processing"] = True
        self.my_data["processing_start_time"] = time.time()
    
    def _stop_processing(self):
        """Stop processing (example method)"""
        logger.info("Stopping processing...")
        # Add your processing logic here
        self.my_data["processing"] = False
        self.my_data["processing_stop_time"] = time.time()
    
    def _reset_node(self):
        """Reset node state (example method)"""
        logger.info("Resetting node...")
        self.my_data.clear()
        self.my_data["reset_time"] = time.time()
    
    def _send_response(self, original_message: NodeMessage, data: Dict[str, Any], addr: tuple):
        """Send response message"""
        response = NodeMessage(
            message_id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            priority=Priority.NORMAL,
            source=self.node_name,
            destination=original_message.source,
            payload=data,
            timestamp=time.time()
        )
        self._send_message(response, addr)
    
    def _send_error_response(self, original_message: NodeMessage, error: str, addr: tuple):
        """Send error response message"""
        response = NodeMessage(
            message_id=str(uuid.uuid4()),
            type=MessageType.RESPONSE,
            priority=Priority.HIGH,
            source=self.node_name,
            destination=original_message.source,
            payload={"error": error},
            timestamp=time.time()
        )
        self._send_message(response, addr)
    
    def get_template_status(self) -> Dict[str, Any]:
        """Get template-specific status"""
        base_status = self.get_status()
        base_status.update({
            "my_timeout": self.my_timeout,
            "data_count": len(self.my_data),
            "background_task_running": self.background_task_running,
            "processing": self.my_data.get("processing", False)
        })
        return base_status

# Global variable to track node instance for signal handler
_node_instance = None
_running = True

def signal_handler(signum, frame):
    """Handle SIGINT and SIGTERM signals for graceful shutdown"""
    global _running
    signal_name = signal.Signals(signum).name
    logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
    _running = False
    if _node_instance:
        _node_instance.stop()

def main():
    """Main entry point for Template Node"""
    global _node_instance, _running
    
    # Register signal handlers for graceful shutdown
    # SIGINT: Ctrl+C or kill -INT
    # SIGTERM: systemd/service manager shutdown or kill -TERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Template Node")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config)
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "node_port": 14560,
            "master_core_host": "localhost",
            "master_core_port": 14550,
            "direct_communication": True,
            "emergency_nodes": [],
            "my_timeout": 30
        }
    
    # Configure logging
    # On Windows daemon mode, ensure errors go to stderr for Master Core to capture
    if args.daemon and platform.system() == 'Windows':
        # Windows daemon: log to stderr so Master Core can capture it
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stderr)]
        )
    else:
        # Normal mode: use default stdout
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create and start node
    node = TemplateNode(config)
    _node_instance = node  # Store for signal handler
    
    if args.daemon:
        # Run as daemon (cross-platform)
        
        # Windows doesn't support python-daemon library
        if platform.system() == 'Windows':
            # Windows: Run in background without daemon library
            # Write PID file to temp directory
            temp_dir = tempfile.gettempdir()
            pid_file = os.path.join(temp_dir, 'template_node.pid')
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            logger.info(f"Running as background process on Windows (PID: {os.getpid()})")
            if node.start():
                logger.info("Template Node started successfully, entering main loop")
                _running = True
                try:
                    while _running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    # Fallback for KeyboardInterrupt
                    logger.info("KeyboardInterrupt received, shutting down")
                    _running = False
            else:
                logger.error("Failed to start Template Node, exiting")
                sys.exit(1)
            node.stop()
        else:
            # Unix/Linux: Use fork approach
            try:
                pid = os.fork()
                if pid > 0:
                    # Parent process - exit
                    sys.exit(0)
            except OSError as e:
                logger.error(f"Failed to fork: {e}")
                sys.exit(1)
            
            # Child process - continue
            os.setsid()  # Create new session
            os.chdir("/")  # Change to root directory
            
            # Write PID file
            with open('/tmp/template_node.pid', 'w') as f:
                f.write(str(os.getpid()))
            
            if node.start():
                logger.info("Template Node started successfully, entering main loop")
                _running = True
                try:
                    while _running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    # Fallback for KeyboardInterrupt
                    logger.info("KeyboardInterrupt received, shutting down")
                    _running = False
            else:
                logger.error("Failed to start Template Node")
                sys.exit(1)
            node.stop()
    else:
        # Run in foreground
        if node.start():
            _running = True
            try:
                while _running:
                    time.sleep(1)
            except KeyboardInterrupt:
                # Fallback for KeyboardInterrupt
                logger.info("KeyboardInterrupt received, shutting down")
                _running = False
        node.stop()

if __name__ == "__main__":
    main()

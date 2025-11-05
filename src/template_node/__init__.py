"""
Template Node Package
Provides BaseNode and related classes for OBS node development
"""

from .base_node import BaseNode, MessageType, Priority, NodeMessage

__all__ = ['BaseNode', 'MessageType', 'Priority', 'NodeMessage']

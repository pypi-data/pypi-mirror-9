from __future__ import absolute_import

from . import ndb, messages, template, settings, hvild
from protorpc.remote import Service
from protorpc.message_types import VoidMessage
from .tool_chain import ToolChain
from .ndb import Model, Behavior
from .messages import model_message, list_message

try:
    from endpoints import get_current_user, NotFoundException, BadRequestException
    from .endpoints import auto_method, auto_service
    from .endpoints import default as default_endpoint
except ImportError as e:
    import logging
    logging.info("Ferris 3: endpoints library not available.")

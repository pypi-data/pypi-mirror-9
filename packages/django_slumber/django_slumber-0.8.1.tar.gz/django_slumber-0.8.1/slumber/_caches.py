"""
    Some caches used in the implementation of the Slumber client or server.
"""
import threading


# Stores the applications via their application names
APP_FROM_APPNAME = {}

# Stores the server model for a given Django model in the server
DJANGO_MODEL_TO_SLUMBER_MODEL = {}
# Stores the slumber models for given model URLs
MODEL_URL_TO_SLUMBER_MODEL = {}

# Store the URIs for special operations
OPERATION_URIS = {}


# Add a location where we can save per thread data
PER_THREAD = threading.local()

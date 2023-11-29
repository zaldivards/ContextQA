
class VectorDBConnectionError(Exception):
    """This exception is raised when a connection could not be established or credentials are invalid"""
    
class DuplicatedSourceError(Exception):
    """Thrown when a source with a same digest already exists"""
class ServiceError(Exception):
    """Base exception for all service errors"""
    pass

# Book-related exceptions
class BookServiceError(ServiceError):
    """Base exception for BookService"""
    pass

class BookNotFoundError(BookServiceError):
    """Raised when a specific book is not found"""
    pass

class BookExistsError(BookServiceError):
    """Raised when attempting to create a book that already exists"""
    pass

class InvalidBookDataError(BookServiceError):
    """Raised when book data fails validation (beyond schema validation)"""
    pass

# S3-related exceptions
class S3ServiceError(ServiceError):
    """Base exception for S3Service"""
    pass

class ThumbnailUploadError(S3ServiceError):
    """Raised when thumbnail upload to S3 fails"""
    pass

class ThumbnailNotFoundError(S3ServiceError):
    """Raised when a thumbnail cannot be found in S3"""
    pass

# Vector database exceptions
class VectorServiceError(ServiceError):
    """Base exception for vector operations (Pinecone)"""
    pass

class VectorEmbeddingError(VectorServiceError):
    """Raised when creating vector embeddings fails"""
    pass

class VectorUpsertError(VectorServiceError):
    """Raised when upserting vectors to Pinecone fails"""
    pass
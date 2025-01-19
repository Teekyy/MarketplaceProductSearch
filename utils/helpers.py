def generate_s3_key(book):
    """
    Generates an S3 key using information from a book JSON object.

    Args:
        book (dict): The JSON object containing book data.

    Returns:
        str: The generated S3 key.
    """
    return book['isbn_13']

def camel_case(text):
    """
    Converts a given string to camel case.

    Args:
        text (str): The input string to be converted.

    Returns:
        str: The camel case version of the input string.
    """
    words = text.split()
    return ''.join([word.capitalize() for word in words])
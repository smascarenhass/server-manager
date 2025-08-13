class FileService:
    """
    Service for file manipulation, including inserting blocks of text.
    
    Example usage:
    file_service = FileService()
    file_path = './test.conf'
    block_of_text = '''
    [main]
     teste
    '''
    
    # Write to a file
    file_service.write_file(file_path, "Line 1\\nLine 2\\n")
    
    # Read the file
    content = file_service.read_file(file_path)
    print("File content after writing:")
    print(content)
    
    # Insert a text block at position 8
    file_service.insert_text_block(file_path, block_of_text, position=8)
    content = file_service.read_file(file_path)
    print("File content after insertion:")
    print(content)
    
    # Check if the file exists
    exists = file_service.file_exists(file_path)
    print(f"Does the file exist? {exists}")
    
    # Delete the file
    # file_service.delete_file(file_path)
    # exists = file_service.file_exists(file_path)
    # print(f"Does the file exist after deletion? {exists}")
    """

    def read_file(self, file_path):
        """
        Reads the content of a file and returns it as a string.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def write_file(self, file_path, content):
        """
        Writes content to a file, overwriting if it already exists.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def insert_text_block(self, file_path, text_block, position=None):
        """
        Inserts a block of text at a specific position in the file.
        If position is None, appends to the end.
        """
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            pass  # File does not exist, will be created

        if position is None or position >= len(content):
            new_content = content + text_block
        else:
            new_content = content[:position] + text_block + content[position:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    def delete_file(self, file_path):
        """
        Deletes the specified file.
        """
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

    def file_exists(self, file_path):
        """
        Checks if the file exists.
        """
        import os
        return os.path.exists(file_path)
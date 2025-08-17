import json

def validate_json_file(filename: str) -> bool:
    """
    Check if a given file is a valid JSON file.

    Args:
        filename (str): The path to the file to be checked.

    Returns:
        bool: True if the file is a valid JSON file, False otherwise.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    
def load_blocks_from_json(filename: str) -> list:
    """
    Load a list of blocks from a JSON file.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        list: A list of blocks loaded from the JSON file.
    """
    try:    
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Error loading JSON file '{filename}': {e}")
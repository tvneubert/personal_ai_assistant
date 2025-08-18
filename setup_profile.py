"""
CLI Interface für Personal AI Assistant Profile Setup
Usage Examples:
  python setup_profile.py nana profile.json                    # Upload profile
  python setup_profile.py nana --setup-conversations           # Setup conversations collection
  python setup_profile.py nana --test-search "ADHS tips"       # Test search functionality
"""

import sys
import os
import argparse
from typing import Final

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.qdrant_client import PersonalAIQdrantClient
from src.utils import validate_json_file

DEFAULT_SEARCH_LIMIT: Final[int] = 3

def upload_profile_command(client: PersonalAIQdrantClient, json_file: str) -> bool:
    print(f"Uploading für user '{client.user_id}' from '{json_file}' ...")

    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found.")
        return False
    
    if not validate_json_file(json_file):
        print(f"Error: '{json_file}' is not a valid JSON file.")
        return False
    try:
        success = client.upload_profile(json_file)
        if success:
            print(f"Profile upload completed!")
        else: 
            print(f"Profile upload failed!")
        return success
    except Exception as e:
        print(f"Unexpected error during profile upload: {e}")
        return False
    
def setup_conversation_command(client: PersonalAIQdrantClient) -> bool:
    print(f"Setting up conversations collection for user '{client.user_id}' ...")

    try:
        success = client.setup_conversation_collection()
        if success:
            print(f"Conversations collection ready!")
        else:
            print(f"Failed to setup conversations collection!")
        return success
    except Exception as e:
        print(f"Unexpected error during conversations setup: {e}")
        return False
    
def main():
    parser = argparse.ArgumentParser(
        description = 'Personal AI Assistant Profile Setup',
        formatter_class = argparse.RawDescriptionHelpFormatter
        )
    
    parser.add_argument('user_id', help='User ID (eg., nana, alex)')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('json_file', nargs='?', help='JSON profile file upload')
    group.add_argument('--setup-conversations', action='store_true',
                       help='Setup conversations collections for the user')
    
    parser.add_argument('--host', default='localhost',
                        help='Qdrant host (default: localhost)')
    parser.add_argument('--port', type=int, default=6333,
                        help='Qdrant port (default: 6333)')
    
    args = parser.parse_args()

    try:
        client = PersonalAIQdrantClient(args.user_id, args.host, args.port)
        print(f"Connected to Qdrant at {args.host}:{args.port}")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        sys.exit(1)
    
    success = False

    if args.json_file:
        success = upload_profile_command(client, args.json_file)
    
    elif args.setup_conversations:
        success = setup_conversation_command(client)
    
    if success:
        print(f"Command completed successfully!")
        sys.exit(0)
    else:
        print(f"Command failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

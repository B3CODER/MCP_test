from .server import main_sse

def main():
    """MCP Reddit Server - Reddit API functionality for MCP"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Run the Reddit MCP server over SSE"
    )
    args = parser.parse_args()
    main_sse()

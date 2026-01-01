# MCP Server Reddit

A Model Context Protocol server providing access to Reddit public API for LLMs. This server enables LLMs to interact with Reddit's content, including browsing frontpage posts, accessing subreddit information, and reading post comments.

This server uses [redditwarp](https://github.com/Pyprohly/redditwarp) to interact with Reddit's public API and exposes the functionality through MCP protocol.


## Available Tools

- `get_frontpage_posts` - Get hot posts from Reddit frontpage
  - Optional arguments:
    - `limit` (integer): Number of posts to return (default: 10, range: 1-100)

- `get_subreddit_info` - Get information about a subreddit
  - Required arguments:
    - `subreddit_name` (string): Name of the subreddit (e.g. 'Python', 'news')

- `get_subreddit_hot_posts` - Get hot posts from a specific subreddit
  - Required arguments:
    - `subreddit_name` (string): Name of the subreddit (e.g. 'Python', 'news')
  - Optional arguments:
    - `limit` (integer): Number of posts to return (default: 10, range: 1-100)

- `get_subreddit_new_posts` - Get new posts from a specific subreddit
  - Required arguments:
    - `subreddit_name` (string): Name of the subreddit (e.g. 'Python', 'news')
  - Optional arguments:
    - `limit` (integer): Number of posts to return (default: 10, range: 1-100)

- `get_subreddit_top_posts` - Get top posts from a specific subreddit
  - Required arguments:
    - `subreddit_name` (string): Name of the subreddit (e.g. 'Python', 'news')
  - Optional arguments:
    - `limit` (integer): Number of posts to return (default: 10, range: 1-100)
    - `time` (string): Time filter for top posts (default: '', options: 'hour', 'day', 'week', 'month', 'year', 'all')

- `get_subreddit_rising_posts` - Get rising posts from a specific subreddit
  - Required arguments:
    - `subreddit_name` (string): Name of the subreddit (e.g. 'Python', 'news')
  - Optional arguments:
    - `limit` (integer): Number of posts to return (default: 10, range: 1-100)

- `get_post_content` - Get detailed content of a specific post
  - Required arguments:
    - `post_id` (string): ID of the post
  - Optional arguments:
    - `comment_limit` (integer): Number of top-level comments to return (default: 10, range: 1-100)
    - `comment_depth` (integer): Maximum depth of comment tree (default: 3, range: 1-10)

- `get_post_comments` - Get comments from a post
  - Required arguments:
    - `post_id` (string): ID of the post
  - Optional arguments:
    - `limit` (integer): Number of comments to return (default: 10, range: 1-100)


## Installation

### Using PIP

```bash
pip install -e .
```

After installation, you can run it as a script using:

```bash
python -m mcp_server_reddit
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<summary>Using pip installation</summary>

```json
"mcpServers": {
  "reddit": {
    "command": "python",
    "args": ["-m", "mcp_server_reddit"]
  }
}
```
</details>

## Examples of Questions

- "What are the current hot posts on Reddit's frontpage?" (get_frontpage_posts)
- "Tell me about the r/ClaudeAI subreddit" (get_subreddit_info)
- "What are the hot posts in the r/ClaudeAI subreddit?" (get_subreddit_hot_posts)
- "Show me the newest posts from r/ClaudeAI" (get_subreddit_new_posts)
- "What are the top posts of all time in r/ClaudeAI?" (get_subreddit_top_posts)
- "What posts are trending in r/ClaudeAI right now?" (get_subreddit_rising_posts)
- "Get the full content and comments of this Reddit post: [post_url]" (get_post_content)
- "Summarize the comments on this Reddit post: [post_url]" (get_post_comments)

## Debugging

You can use the MCP inspector to debug the server. 

```bash
cd path/to/mcp_server_reddit
npx @modelcontextprotocol/inspector uv run mcp-server-reddit
```

and then in the inspector, point to:
```
http://127.0.0.1:8001/sse

```
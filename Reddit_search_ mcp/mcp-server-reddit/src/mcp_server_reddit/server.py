from enum import Enum
import json
from typing import Optional
import redditwarp.SYNC
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import argparse
import uvicorn
import sys


# ----------------------
# Enums and Models
# ----------------------

class PostType(str, Enum):
    LINK = "link"
    TEXT = "text"
    GALLERY = "gallery"
    UNKNOWN = "unknown"


class SubredditInfo(BaseModel):
    name: str
    subscriber_count: int
    description: Optional[str]


class Post(BaseModel):
    id: str
    title: str
    author: str
    score: int
    subreddit: str
    url: str
    created_at: str
    comment_count: int
    post_type: PostType
    content: Optional[str]


class Comment(BaseModel):
    id: str
    author: str
    body: str
    score: int
    replies: list["Comment"] = []


class PostDetail(BaseModel):
    post: Post
    comments: list[Comment]


# ----------------------
# Reddit Client Wrapper
# ----------------------

class RedditServer:
    def __init__(self):
        self.client = redditwarp.SYNC.Client()

    def _get_post_type(self, submission) -> PostType:
        if isinstance(submission, redditwarp.models.submission_SYNC.LinkPost):
            return PostType.LINK
        elif isinstance(submission, redditwarp.models.submission_SYNC.TextPost):
            return PostType.TEXT
        elif isinstance(submission, redditwarp.models.submission_SYNC.GalleryPost):
            return PostType.GALLERY
        return PostType.UNKNOWN

    def _get_post_content(self, submission) -> Optional[str]:
        if isinstance(submission, redditwarp.models.submission_SYNC.LinkPost):
            return submission.permalink
        elif isinstance(submission, redditwarp.models.submission_SYNC.TextPost):
            return submission.body
        elif isinstance(submission, redditwarp.models.submission_SYNC.GalleryPost):
            return str(submission.gallery_link)
        return None

    def _build_post(self, submission) -> Post:
        return Post(
            id=submission.id36,
            title=submission.title,
            author=submission.author_display_name or "[deleted]",
            score=submission.score,
            subreddit=submission.subreddit.name,
            url=submission.permalink,
            created_at=submission.created_at.astimezone().isoformat(),
            comment_count=submission.comment_count,
            post_type=self._get_post_type(submission),
            content=self._get_post_content(submission),
        )

    def get_frontpage_posts(self, limit: int = 10) -> list[Post]:
        return [self._build_post(s) for s in self.client.p.front.pull.hot(limit)]

    def get_subreddit_info(self, subreddit_name: str) -> SubredditInfo:
        subr = self.client.p.subreddit.fetch_by_name(subreddit_name)
        return SubredditInfo(
            name=subr.name,
            subscriber_count=subr.subscriber_count,
            description=subr.public_description,
        )

    def _build_comment_tree(self, node, depth: int = 3) -> Optional[Comment]:
        if depth <= 0 or not node:
            return None
        comment = node.value
        replies = []
        for child in node.children:
            child_comment = self._build_comment_tree(child, depth - 1)
            if child_comment:
                replies.append(child_comment)
        return Comment(
            id=comment.id36,
            author=comment.author_display_name or "[deleted]",
            body=comment.body,
            score=comment.score,
            replies=replies,
        )

    def get_subreddit_hot_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        return [self._build_post(s) for s in self.client.p.subreddit.pull.hot(subreddit_name, limit)]

    def get_subreddit_new_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        return [self._build_post(s) for s in self.client.p.subreddit.pull.new(subreddit_name, limit)]

    def get_subreddit_top_posts(self, subreddit_name: str, limit: int = 10, time: str = "") -> list[Post]:
        return [self._build_post(s) for s in self.client.p.subreddit.pull.top(subreddit_name, limit, time=time)]

    def get_subreddit_rising_posts(self, subreddit_name: str, limit: int = 10) -> list[Post]:
        return [self._build_post(s) for s in self.client.p.subreddit.pull.rising(subreddit_name, limit)]

    def get_post_content(self, post_id: str, comment_limit: int = 10, comment_depth: int = 3) -> PostDetail:
        submission = self.client.p.submission.fetch(post_id)
        post = self._build_post(submission)
        comments = self.get_post_comments(post_id, comment_limit, comment_depth)
        return PostDetail(post=post, comments=comments)

    def get_post_comments(self, post_id: str, limit: int = 10, depth: int = 3) -> list[Comment]:
        tree_node = self.client.p.comment_tree.fetch(post_id, sort="top", limit=limit)
        comments = []
        for node in tree_node.children:
            comment = self._build_comment_tree(node, depth)
            if comment:
                comments.append(comment)
        return comments


# ----------------------
# FastMCP SSE Server
# ----------------------

mcp = FastMCP("Reddit MCP Server")
reddit_server = RedditServer()


@mcp.tool()
def get_frontpage_posts(limit: int = 10) -> str:
    result = reddit_server.get_frontpage_posts(limit)
    return json.dumps([p.model_dump() for p in result], indent=2)


@mcp.tool()
def get_subreddit_info(subreddit_name: str) -> str:
    result = reddit_server.get_subreddit_info(subreddit_name)
    return result.model_dump_json(indent=2)


@mcp.tool()
def get_subreddit_hot_posts(subreddit_name: str, limit: int = 10) -> str:
    result = reddit_server.get_subreddit_hot_posts(subreddit_name, limit)
    return json.dumps([p.model_dump() for p in result], indent=2)


@mcp.tool()
def get_subreddit_new_posts(subreddit_name: str, limit: int = 10) -> str:
    result = reddit_server.get_subreddit_new_posts(subreddit_name, limit)
    return json.dumps([p.model_dump() for p in result], indent=2)


@mcp.tool()
def get_subreddit_top_posts(subreddit_name: str, limit: int = 10, time: str = "") -> str:
    result = reddit_server.get_subreddit_top_posts(subreddit_name, limit, time)
    return json.dumps([p.model_dump() for p in result], indent=2)


@mcp.tool()
def get_subreddit_rising_posts(subreddit_name: str, limit: int = 10) -> str:
    result = reddit_server.get_subreddit_rising_posts(subreddit_name, limit)
    return json.dumps([p.model_dump() for p in result], indent=2)


@mcp.tool()
def get_post_content(post_id: str, comment_limit: int = 10, comment_depth: int = 3) -> str:
    result = reddit_server.get_post_content(post_id, comment_limit, comment_depth)
    return result.model_dump_json(indent=2)


@mcp.tool()
def get_post_comments(post_id: str, limit: int = 10, depth: int = 3) -> str:
    result = reddit_server.get_post_comments(post_id, limit, depth)
    return json.dumps([c.model_dump() for c in result], indent=2)


# ----------------------
# Entry Point
# ----------------------

def main_sse():
    parser = argparse.ArgumentParser(description="Reddit MCP Server (SSE)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)  # use 8001 to avoid clash with Google Calendar
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args()

    print(f"🌐 Server starting on http://{args.host}:{args.port}")
    print(f"📡 SSE endpoint: http://{args.host}:{args.port}/sse")

    app = mcp.sse_app()
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main_sse()

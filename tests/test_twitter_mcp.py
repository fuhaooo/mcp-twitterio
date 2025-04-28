"""
Twitter API MCP服务的测试
"""
import os
import pytest
from mcp.server.fastmcp import FastMCP
from main import mcp


def test_mcp_instance():
    """测试MCP实例是否正确创建"""
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "TwitterAPI Client"


def test_tools_registered():
    """测试工具是否正确注册"""
    required_tools = [
        "get_user_info_by_username",
        "batch_get_users_by_ids",
        "get_user_last_tweets",
        "get_user_followers",
        "get_user_followings",
        "get_user_mentions",
        "get_tweets_by_ids",
        "get_tweet_replies",
        "get_tweet_quotations",
        "get_tweet_retweeters",
        "get_list_tweets",
        "advanced_search_tweets"
    ]
    
    tool_names = [tool.name for tool in mcp.list_tools_sync()]
    for tool in required_tools:
        assert tool in tool_names, f"工具 '{tool}' 未注册"


@pytest.mark.skipif(not os.environ.get("TWITTER_API_KEY"), 
                    reason="需要设置TWITTER_API_KEY环境变量")
def test_env_variables():
    """测试环境变量是否正确设置"""
    assert os.environ.get("TWITTER_API_KEY"), "TWITTER_API_KEY环境变量未设置" 
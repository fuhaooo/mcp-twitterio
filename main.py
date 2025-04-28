#!/usr/bin/env python
"""
Twitter API MCP服务

基于twitterapi.io API的MCP服务，使用studio模式进行通信
"""
import os
import httpx
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Union

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    # 尝试加载.env文件或env文件
    if Path('.env').exists():
        load_dotenv('.env')
    elif Path('env').exists():
        load_dotenv('env')
except ImportError:
    print("提示: 安装python-dotenv包可以从.env文件加载环境变量")

# 创建一个MCP服务器，以studio模式运行
mcp = FastMCP("TwitterAPI Client", dependencies=["httpx>=0.28.1", "python-dotenv>=1.0.0"])

# Twitter API基础URL
BASE_URL = "https://api.twitterapi.io"

# 获取API密钥，从环境变量或配置文件
API_KEY = os.environ.get("TWITTER_API_KEY", "")

# Debug模式
DEBUG = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")


# 创建HTTP客户端
async def get_client():
    """创建一个配置好的HTTP客户端"""
    if DEBUG:
        print(f"DEBUG: 创建HTTP客户端连接到 {BASE_URL}")
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"}
    )


@mcp.tool()
async def get_user_info_by_username(userName: str, ctx: Context = None) -> dict:
    """根据用户名Handle获取用户信息
    
    Args:
        username: Twitter用户名Handle（不含@符号）
    
    Returns:
        包含用户信息的字典
    """
    if ctx:
        await ctx.info(f"获取用户信息: {userName}")
        
    async with await get_client() as client:
        response = await client.get(f"/twitter/user/info?userName={userName}")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def batch_get_users_by_ids(user_ids: str, ctx: Context = None) -> dict:
    """根据用户ID批量获取用户信息
    
    Args:
        user_ids: 用逗号分隔的用户ID列表，例如："1234567890,1234567891,1234567892"
    
    Returns:
        包含多个用户信息的字典
    """
    if ctx:
        await ctx.info(f"批量获取用户信息: {user_ids}")
        
    async with await get_client() as client:
        response = await client.get(f"/twitter/user/batch_info_by_ids?userIds={user_ids}")
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_user_last_tweets(userId: str = "", userName: str = "", cursor: str = "", ctx: Context = None) -> dict:
    """获取用户最新的推文
    
    Args:
        userId: 用户ID (推荐使用，更稳定更快)
        userName: 用户名称（screen name）
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含用户推文的字典
    """
    if ctx:
        if userId:
            await ctx.info(f"获取用户ID {userId} 的最新推文")
        elif userName:
            await ctx.info(f"获取用户 {userName} 的最新推文")
    
    # userId和userName至少需要提供一个
    if not userId and not userName:
        raise ValueError("userId和userName至少需要提供一个")
    
    params = {}
    if userId:
        params["userId"] = userId
    if userName and not userId:  # 如果同时提供了userId和userName，将使用userId
        params["userName"] = userName
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/user/last_tweets", params=params)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_user_followers(userName: str, cursor: str = "", ctx: Context = None) -> dict:
    """获取用户的粉丝列表
    
    Args:
        userName: 用户名称（screen name）(必需)
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含用户粉丝列表的字典，每页返回最多200个粉丝
    """
    if ctx:
        await ctx.info(f"获取用户 {userName} 的粉丝列表")
    
    params = {
        "userName": userName
    }
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/user/followers", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_user_followings(userName: str, cursor: str = "", ctx: Context = None) -> dict:
    """获取用户的关注列表
    
    Args:
        userName: 用户名称（screen name）(必需)
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含用户关注列表的字典，每页返回最多200个关注用户
    """
    if ctx:
        await ctx.info(f"获取用户 {userName} 的关注列表")
    
    params = {
        "userName": userName
    }
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/user/followings", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_user_mentions(userName: str, sinceTime: int = None, untilTime: int = None, cursor: str = "", ctx: Context = None) -> dict:
    """获取用户的提及
    
    Args:
        userName: 用户名称（screen name）(必需)
        sinceTime: 在指定的unix时间戳（秒）之后
        untilTime: 在指定的unix时间戳（秒）之前
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含用户提及的推文列表，每页返回最多20条提及
    """
    if ctx:
        await ctx.info(f"获取用户 {userName} 的提及")
    
    params = {
        "userName": userName
    }
    if sinceTime is not None:
        params["sinceTime"] = sinceTime
    if untilTime is not None:
        params["untilTime"] = untilTime
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/user/mentions", params=params)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_tweets_by_ids(tweet_ids: str, ctx: Context = None) -> dict:
    """通过推文ID获取推文
    
    Args:
        tweet_ids: 推文ID列表，多个ID用逗号分隔，例如"1846987139428634858,1866332309399781537"
    
    Returns:
        包含推文列表的字典
    """
    if ctx:
        await ctx.info(f"获取推文信息: {tweet_ids}")
    
    params = {
        "tweet_ids": tweet_ids
    }
    
    async with await get_client() as client:
        response = await client.get("/twitter/tweets", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_tweet_replies(tweetId: str, sinceTime: int = None, untilTime: int = None, cursor: str = "", ctx: Context = None) -> dict:
    """获取推文的回复
    
    Args:
        tweetId: 推文ID（必须是原始推文，非回复）
        sinceTime: 在指定的unix时间戳（秒）之后
        untilTime: 在指定的unix时间戳（秒）之前
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含回复推文的字典，每页返回最多20条回复
    """
    if ctx:
        await ctx.info(f"获取推文 {tweetId} 的回复")
    
    params = {
        "tweetId": tweetId
    }
    if sinceTime is not None:
        params["sinceTime"] = sinceTime
    if untilTime is not None:
        params["untilTime"] = untilTime
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/tweet/replies", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_tweet_quotations(tweetId: str, sinceTime: int = None, untilTime: int = None, includeReplies: bool = True, cursor: str = "", ctx: Context = None) -> dict:
    """获取引用推文的推文
    
    Args:
        tweetId: 推文ID
        sinceTime: 在指定的unix时间戳（秒）之后
        untilTime: 在指定的unix时间戳（秒）之前
        includeReplies: 是否包含回复，默认为True
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含引用推文的字典，每页返回最多20条引用
    """
    if ctx:
        await ctx.info(f"获取引用推文 {tweetId} 的推文")
    
    params = {
        "tweetId": tweetId
    }
    if sinceTime is not None:
        params["sinceTime"] = sinceTime
    if untilTime is not None:
        params["untilTime"] = untilTime
    if not includeReplies:
        params["includeReplies"] = "false"
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/tweet/quotes", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_tweet_retweeters(tweetId: str, cursor: str = "", ctx: Context = None) -> dict:
    """获取转发推文的用户
    
    Args:
        tweetId: 推文ID
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含转发用户列表的字典，每页返回约100个用户
    """
    if ctx:
        await ctx.info(f"获取转发推文 {tweetId} 的用户")
    
    params = {
        "tweetId": tweetId
    }
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/tweet/retweeters", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def advanced_search_tweets(query: str, queryType: str = "Latest", cursor: str = "", ctx: Context = None) -> dict:
    """高级搜索推文
    
    Args:
        query: 搜索查询语句，例如 "AI OR Twitter from:elonmusk since:2021-12-31_23:59:59_UTC"
        queryType: 搜索类型，可选 "Latest" 或 "Top"，默认为 "Latest"
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含搜索结果的字典，每页返回约20条推文
    """
    if ctx:
        await ctx.info(f"高级搜索推文: {query} (类型: {queryType})")
    
    params = {
        "query": query,
        "queryType": queryType
    }
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/tweet/advanced_search", params=params)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_list_tweets(listId: str, sinceTime: int = None, untilTime: int = None, includeReplies: bool = True, cursor: str = "", ctx: Context = None) -> dict:
    """获取列表中的推文
    
    Args:
        listId: 列表ID
        sinceTime: 在指定的unix时间戳（秒）之后
        untilTime: 在指定的unix时间戳（秒）之前
        includeReplies: 是否包含回复，默认为True
        cursor: 用于分页的游标，第一页为空字符串
    
    Returns:
        包含列表推文的字典，每页返回最多20条推文
    """
    if ctx:
        await ctx.info(f"获取列表 {listId} 中的推文")
    
    params = {
        "listId": listId
    }
    if sinceTime is not None:
        params["sinceTime"] = sinceTime
    if untilTime is not None:
        params["untilTime"] = untilTime
    if not includeReplies:
        params["includeReplies"] = "false"
    if cursor:
        params["cursor"] = cursor
    
    async with await get_client() as client:
        response = await client.get("/twitter/list/tweets", params=params)
        response.raise_for_status()
        return response.json()

# 检查API密钥是否已设置
if not API_KEY:
    print("警告: 未设置TWITTER_API_KEY环境变量。请设置API密钥以使用推特API功能。")
    print("提示: 您可以创建.env文件并添加 TWITTER_API_KEY=your_key_here")


def main():
    """启动MCP服务"""
    print("启动Twitter API MCP服务...")
    mcp.run()


if __name__ == "__main__":
    main()

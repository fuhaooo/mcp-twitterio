#!/usr/bin/env python
"""
Twitter API MCP 客户端示例

此示例展示如何从Python代码中使用Twitter API MCP服务。
"""
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 设置服务参数
server_params = StdioServerParameters(
    command="python",  # 使用Python解释器
    args=["../main.py"],  # MCP服务脚本路径
    env={"TWITTER_API_KEY": os.environ.get("TWITTER_API_KEY", "")},  # 传递API密钥
)


async def main():
    """主函数，展示MCP客户端使用"""
    print("连接到Twitter API MCP服务...")
    
    # 连接到MCP服务
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 列出可用工具
            print("\n获取可用工具:")
            tools = await session.list_tools()
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            # 获取用户信息
            username = "elonmusk"  # 示例用户名
            print(f"\n获取用户 '{username}' 的信息:")
            try:
                result = await session.call_tool("get_user_info_by_username", {"userName": username})
                print(json.dumps(result.content[0].content, indent=2))
            except Exception as e:
                print(f"获取用户信息失败: {e}")
            
            # 获取用户最新推文
            print(f"\n获取用户 '{username}' 的最新推文:")
            try:
                result = await session.call_tool("get_user_last_tweets", {"userName": username})
                print(json.dumps(result.content[0].content, indent=2))
            except Exception as e:
                print(f"获取用户推文失败: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 
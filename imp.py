import asyncio
from langchain_groq import ChatGroq
from  dotenv import load_dotenv
from mcp_use import MCPClient,MCPAgent
import os


async def run_memeory_chat():
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    config_file="browser_mcp.json"

    print("Starting MCP Server...")

    client= MCPClient.from_config_file(config_file)
    llm= ChatGroq(model="llama-3.1-8b-instant")
    agent=MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True

    )
    print("MCP Server started successfully.")
    print("Starting chat...")

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chat...")
                break
            
            print("\nAssistant: ", end="", flush=True)

            try:
                response = await agent.run(user_input)
                print(response)
            except Exception as e:
                print(f"Error during chat: {e}")
    finally:
        if client and client.is_connected():
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_memeory_chat())
    
"""
RAG Agent for the Chatbot Backend (OpenAI AgentSDK Approach).
Implements an agent that retrieves relevant content and generates responses using openai-agents SDK.
"""
import os
import sys
import dotenv
import asyncio


# Add the backend directory to the path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from src.utils.logger import get_logger, log_info, log_error
from agents import Agent, Runner,set_tracing_disabled,AsyncOpenAI,OpenAIChatCompletionsModel
# from agents.extensions.models.litellm_model import LitellmModel
from agents.run import RunConfig


# Initialize logger
# logger = get_logger(__name__)

# Disable tracing for cleaner output
set_tracing_disabled(disabled=True)
dotenv.load_dotenv()

# Set up environment variables for API keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    tracing_disabled=True
)



# Define the RAG Agent
book_rag_agent = Agent(
    name='Book RAG Assistant',
    model="gemini-2.5-flash",
    instructions="""You are a helpful assistant for the PhysicalAI humanoid robotics book.
    Use the retrieve_book_content tool to find relevant information from the book to answer user questions.
    Always provide clear, concise answers based on the book content you retrieve.""",
    # tools=[retrieve_book_content]
)


async def main_agent():
    """
    Main function to run the RAG agent interactively.
    """
    # log_info("Starting RAG Agent with AgentSDK...")

    print("Book RAG Agent is ready! Ask questions about the PhysicalAI humanoid robotics book content.")
    print("Type 'quit' or 'exit' to stop.\n")

    runner = Runner()
    while True:
        try:
            user_input = input("Your question: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            if not user_input:
                print("Please ask a question.\n")
                continue

            run_result = await runner.run(starting_agent=book_rag_agent, input=user_input,run_config=config)
            if hasattr(run_result, 'output') and run_result.output:
                response = run_result.output
            elif isinstance(run_result, str):
                response = run_result
            else:
                response = str(run_result)

            print(f"Answer: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            # log_error(f"Error in main agent loop: {str(e)}")
            print("An error occurred. Please try again.\n")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main_agent())
    except KeyboardInterrupt:
        print("Agent stopped.")
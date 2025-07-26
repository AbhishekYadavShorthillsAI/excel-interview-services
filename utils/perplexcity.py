import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

class PerplexityClient:
    def __init__(self, model="sonar", temperature=0.0, max_tokens=1024):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = os.getenv("PERPLEXITY_BASE_URL")


        if not self.api_key:
            raise ValueError("Please set the PERPLEXITY_API_KEY environment variable.")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    async def invoke(self, query, system_prompt=None):
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": query})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": query}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content


# ---- Test Code ----
# async def main():
#     client = PerplexityClient()
#     query = "What is the capital of France?"
#     result = await client.invoke(query)
#     print("Response:", result)

# if __name__ == "__main__":
#     asyncio.run(main())

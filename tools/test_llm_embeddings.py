import os
from dotenv import load_dotenv
import cohere

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def test_llm():
    response = co.chat(
        message="Say hello!",
        model="command-a-03-2025"
    )

    print("Chat Response:")
    print(response.text)

def test_embeddings():
    response = co.embed(
        model="embed-english-v3.0",
        texts=["Hello, this is a test!"]
    )

    print("\nEmbeddings Response:")
    print(response.embeddings[0][:10])

if __name__ == "__main__":
    test_llm()
    test_embeddings()

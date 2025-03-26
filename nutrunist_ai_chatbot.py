import os
import openai

# Option 1: Set your API key as an environment variable named "OPENAI_API_KEY"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Option 2: Directly assign your API key (be cautious with hardcoding keys)
openai.api_key = "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"

def chat():
    # Start with a system prompt for context
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    
    print("Welcome to Nutrunist AI Chatbot!")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Ending the conversation. Goodbye!")
            break
        
        # Append user message to conversation history
        conversation.append({"role": "user", "content": user_input})
        
        try:
            # Call the chat endpoint using the updated API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation,
                temperature=0.7
            )
            # Extract and print the assistant's reply
            answer = response.choices[0].message.content
            print("Assistant:", answer, "\n")
            
            # Append the assistant's reply to the conversation history
            conversation.append({"role": "assistant", "content": answer})
        
        except Exception as e:
            print("Error communicating with OpenAI:", e)
            break

if __name__ == "__main__":
    chat()

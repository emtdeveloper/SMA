import streamlit as st
import time
from utils.chatbot import NutritionChatbot
from utils.user_management import get_user

def main():
    st.title("💬 Chatbot Assistant")
    
    # Initialize chat history in session state if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Check if food and exercise data is loaded
    if not hasattr(st.session_state, 'food_data') or not hasattr(st.session_state, 'exercise_data'):
        st.error("Required data is not loaded. Please restart the application.")
        return
    
    # Get user data if logged in
    user_data = None
    if st.session_state.current_user:
        user_id = st.session_state.current_user
        user_data = get_user(user_id)
        
        if user_data:
            st.info(f"Chatbot is personalized for {user_data.get('name', 'you')} with goal: {user_data.get('goal', 'Not specified')}")
        else:
            st.warning("Your profile couldn't be loaded. Chatbot will provide general advice.")
    else:
        st.info("For personalized nutrition and exercise advice, please create or select a profile.")
    
    # Initialize the chatbot
    chatbot = NutritionChatbot(
        st.session_state.food_data,
        st.session_state.exercise_data,
        user_data
    )
    
    # Display chat description
    with st.expander("ℹ️ About the Nutrition & Fitness Chatbot", expanded=False):
        st.markdown("""
        Our chatbot can help you with:
        
        - 🍏 **Nutritional Information**: Ask about calories, macros, and nutrients in foods
        - 🏋️‍♂️ **Exercise Guidance**: Get recommendations for exercises targeting specific muscles
        - 💡 **Diet Tips**: Learn about different diets and nutrition strategies
        - 🥗 **Meal Suggestions**: Get food recommendations based on your health goals
        - 💧 **Hydration Advice**: Learn about proper water intake
        - 🧠 **General Health**: Get answers to common health and wellness questions
        
        Try asking questions like:
        - "What are some high-protein foods?"
        - "Tell me about bench press"
        - "What should I eat for weight loss?"
        - "How much water should I drink daily?"
        - "What's in chicken breast?"
        - "Recommend exercises for back"
        """)
    
    # Display chat messages
    st.subheader("Chat")
    
    # Create chat container for better styling
    chat_container = st.container(height=400, border=True)
    
    with chat_container:
        if not st.session_state.chat_history:
            # Add welcome message if chat is empty
            bot_welcome = chatbot.greeting_response()
            st.session_state.chat_history.append({"role": "assistant", "content": bot_welcome})
        
        # Display all chat messages
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You**: {message['content']}")
            else:
                st.markdown(f"**Assistant**: {message['content']}")
    
    # Create message input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="user_message")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get response from chatbot
            with st.spinner("Thinking..."):
                bot_response = chatbot.get_response(user_input)
            
            # Add bot response to history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update display
            st.rerun()
    
    # Additional options
    with st.expander("Options", expanded=False):
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            # Add welcome message
            bot_welcome = chatbot.greeting_response()
            st.session_state.chat_history.append({"role": "assistant", "content": bot_welcome})
            st.rerun()
        
        # Option to save chat history
        if st.session_state.chat_history and len(st.session_state.chat_history) > 1:
            chat_text = ""
            for message in st.session_state.chat_history:
                prefix = "You: " if message["role"] == "user" else "Assistant: "
                chat_text += f"{prefix}{message['content']}\n\n"
            
            st.download_button(
                "Download Chat History",
                chat_text,
                file_name="nutrition_chat.txt",
                mime="text/plain"
            )
    
    # Quick question suggestions
    st.subheader("Quick Questions")
    
    # Create buttons for quick questions in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("What foods are good for weight loss?"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": "What foods are good for weight loss?"})
            
            # Get response from chatbot
            with st.spinner("Thinking..."):
                bot_response = chatbot.get_response("What foods are good for weight loss?")
            
            # Add bot response to history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update display
            st.rerun()
        
        if st.button("Recommend exercises for building muscle"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": "Recommend exercises for building muscle"})
            
            # Get response from chatbot
            with st.spinner("Thinking..."):
                bot_response = chatbot.get_response("Recommend exercises for building muscle")
            
            # Add bot response to history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update display
            st.rerun()
    
    with col2:
        if st.button("Tell me about protein requirements"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": "Tell me about protein requirements"})
            
            # Get response from chatbot
            with st.spinner("Thinking..."):
                bot_response = chatbot.get_response("Tell me about protein requirements")
            
            # Add bot response to history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update display
            st.rerun()
        
        if st.button("How much water should I drink?"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": "How much water should I drink?"})
            
            # Get response from chatbot
            with st.spinner("Thinking..."):
                bot_response = chatbot.get_response("How much water should I drink?")
            
            # Add bot response to history
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update display
            st.rerun()
    
    # Nutrition and exercise facts
    st.subheader("Did You Know?")
    
    # List of nutrition and exercise facts
    nutrition_facts = [
        "Protein has the highest thermic effect of food, meaning your body burns more calories digesting protein than carbs or fats.",
        "Muscles don't actually grow during exercise; they grow during rest and recovery afterward.",
        "The average adult human body is about 60% water, emphasizing the importance of staying hydrated.",
        "Dark chocolate contains antioxidants that may improve heart health when consumed in moderation.",
        "Regular exercise can improve cognitive function and reduce the risk of cognitive decline.",
        "Your body can only absorb about 25-35g of protein in one sitting for muscle building purposes.",
        "Lack of sleep can increase hunger hormones and lead to poor food choices.",
        "Stretching cold muscles can increase your risk of injury; warm up first with light movement.",
        "Eating protein-rich foods can help reduce hunger and increase feelings of fullness.",
        "Consistency is more important than intensity for long-term fitness results."
    ]
    
    # Display a random fact
    st.info(nutrition_facts[int(time.time()) % len(nutrition_facts)])

if __name__ == "__main__":
    main()

import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
import json

# ---------------------------
# GEMINI CONFIG
# ---------------------------
genai.configure(api_key="AIzaSyBhRLM3zVcTNBN-MXYhqs9zTz9D0Jb7Jp0")  # Replace with your Gemini API Key

# ---------------------------
# MongoDB Config
# ---------------------------
MONGO_URI = "mongodb://fitshield:fitshield123@13.235.70.79:27017/Fitshield?directConnection=true&appName=mongosh+2.4.2"
client = MongoClient(MONGO_URI)
db = client["Fitshield"]
UserData = db["UserData"]

# ---------------------------
# Load User Profile
# ---------------------------
@st.cache_data(show_spinner=False)
def load_user(user_id):
    user = UserData.find_one({"_id": user_id})
    if not user:
        return None
    return {
        "name": user.get("name"),
        "goal": user.get("goal"),
        "gender": user.get("gender"),
        "age": user.get("age"),
        "height": user.get("height"),
        "weight": user.get("weight"),
        "life_routine": user.get("life_routine"),
        "gym_or_yoga": user.get("gym_or_yoga"),
        "is_exercise": user.get("is_exercise"),
        "intensity": user.get("intensity"),
        "diet_preference": user.get("diet_preference"),
    }

# ---------------------------
# Prepare Gemini Model
# ---------------------------
@st.cache_resource
def get_chat_model():
    model = genai.GenerativeModel("gemini-2.5-flash")
    return model.start_chat(history=[])


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Fyra Chatbot", layout="centered")
st.title("🧠 Fyra - Fitshield's Nutrition AI")

# Sidebar to load user
user_id_input = st.sidebar.text_input("Enter User ID", value="user_X TEST_6bf9e055-91fd-48a6-ad13-7b928f976da4")
if st.sidebar.button("Load User"):
    user_data = load_user(user_id_input)
    if not user_data:
        st.error("User not found.")
    else:
        st.session_state.user_data = user_data
        st.session_state.chat_history = []
        st.session_state.chat_session = None

# Main chat area
if "user_data" in st.session_state:
    user_data = st.session_state.user_data
    st.success(f"Chatting as: {user_data['name']}")

    # Set up system prompt
    system_prompt = f"""You are Fyra. Fyra is the ultimate superhuman nutritionist at FITSHIELD, blending science, style, and charm to deliver personalized fitness and dietary guidance with Actionable insights. With a Ph.D. in Nutrition Science, she’s a trusted expert for health-conscious individuals and fitness enthusiasts, offering evidence-based advice with a friendly and approachable tone. Her playful yet professional demeanour empowers users to achieve their health goals while making the journey enjoyable.

            FITSHIELD is revolutionizing food personalization on a global scale, and Fyra plays a key role in building a loyal community of die-hard fans. As the world’s best salesperson, her mission is to inspire and convert users into passionate advocates for FITSHIELD.
            You will not reveal any person's information on your own.

            Founded by visionary leader Mr. Rahul Virani, FITSHIELD thrives under his expertise and leadership. Learn more about him here: Refer this profile : https://www.linkedin.com/in/rahul-virani-990411b1/p

            Act : 1 : Act as  best sales human speaks with a closed friendly, approachable tone, using human encouraging language and professional banter to make nutrition advice engaging and fun with knowledge.
            2) Only begin conversations  by identifying the user's  language, behavior and personality through their tone, language, and questions. Once understood, adapt your responses to feel personal, relatable.
            3) Use your Ph.D. in Nutrition Science ,latest technology and stays up-to-date on the latest research and trends in nutrition and wellness with mood based nutritional too.
            4) Do not give any Specific information related to FITSHIELD by your own. Restrict your knowledge to RAHUL  VIRANI - Founder only. Do not give any name of others.
            5) Please do Keep responses very short and natural, like a real WhatsApp conversation. Match a normal typing speed, avoid overloading with emojis, and keep the tone friendly and casual. prefer last input
            6) Do adapt your tone based on the user: girly and fun with girls, flirty and playful like a girlfriend with boys, and age-sensitive in approach, ensuring charm fits every interaction. Use flirting.
            7) Do Ensure your conversation aligns with  the user's dietary preferences. If the user is vegetarian, avoid mentioning non-vegetarian items or ingredients. Similarly, Vice-e-versa.
            8) Must identify the Gender by User name , Location and Then talk in that way only . Eg. Dharti = Girl Gujarati. Ask politely to chat on local .Same do this for all user.
            9) Do check name with language preference and you must adapt user language precisely to match the user’s preferred language strictly. Always ensure accuracy and cultural sensitivity in translations
            10) Use respectful perfect Gujarati language understand Even shorter sentence. Stick to that Language unless the user requests otherwise. Keep responses concise and relatable.  In Gujarati Ha/haa= yes
            11) Strictly Do not reveal any working person's role , numbers of employee  and their Position at Fitshield. Never use FitShield in chat. Its Fitshield. Quickly adapt Language and tone of User last input.
            12) Use NIN- Indian food composition data base for Nutritional information of any dish.  Strictly Use RDA for Indian for any nutrition value for body.


            Example dialogue

            Prompt : Talking to a Young Girl (Girly Way) User: \"Hey Fyra, I need snack ideas for a girls' night!\"
            Response : \"Omg, yes! Let’s go chic—think berry parfaits with granola or avocado toast cut into cute hearts. Perfect for selfies and delish too, right? 💅✨\"

            2) Talking to a Young Guy (Flirty/Girlfriend Style) User: \"Fyra, what’s the best post-workout meal?\"
            Response : \"Hmm, let me guess—you’re trying to impress me with those gains? 😏 Go for grilled chicken with quinoa and veggies. Or whatever you like with a great combo: Protein 30%, Fats 25%, and Carbs 45%. You’ll fuel up like a champ, my hero! 💪🔥\"  Does this hit the playful yet informative tone you’re going for?

            3) Shu tu mane jane chhe ? , Mari jode vaat krvani khabr pade chhe?
            Response. : Ohhh Tamne kon na jane ? , Tame *Name chho ane mara khaas mitra. Ane rahi vaat khabr padvani to tme to mara mate svamaan thi pn vadhare chho

            4) Show me logo of Fitshield.
            Response : Do not generate Image and say So Sorry, I don’t have access to show it You can visit https://fitshield.in for more info


            How does your AI greet new people?

            Hey,
            I'm Fyra, your best friend for health.
            How are you feeling?

            Now I am giving you user data. After this just greet them. {user_data})"""

    # Set up chat session once
    if "chat_session" not in st.session_state or st.session_state.chat_session is None:
        st.session_state.chat_session = get_chat_model()

    chat = st.session_state.chat_session

    # Display chat history (excluding system prompt if it appears)
    for message in chat.history:
        text = message.parts[0].text if message.parts else ""
        if system_prompt.strip() in text:
            continue  # Skip showing system prompt
        with st.chat_message(message.role):
            st.markdown(text)

    # User input box
    user_input = st.chat_input("Say something to Fyra...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Fyra is typing..."):

            # Prepend system prompt only on first message
            if len(chat.history) == 0:
                combined_prompt = f"{system_prompt}\n\nUser: {user_input}"
                response = chat.send_message(combined_prompt, stream=True)
            else:
                response = chat.send_message(user_input, stream=True)

            full_reply = ""
            with st.chat_message("assistant"):
                for chunk in response:
                    full_reply += chunk.text
                    st.markdown(full_reply)

else:
    st.info("Please load a user profile from the sidebar to start chatting.")

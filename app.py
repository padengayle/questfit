import streamlit as st
import requests

# 1. Configure the Page
st.set_page_config(page_title="QuestFit RPG", page_icon="⚔️", layout="centered")

st.title("⚔️ QuestFit: AI Fitness RPG")
st.markdown("Transform your unstructured, messy workout logs into structured RPG stats.")

# 2. The User Input Area
st.subheader("Log Your Training")
workout_input = st.text_area(
    "Paste your raw workout log here:",
    value="Crushed a 15 min AMRAP in Astoria today. 15 kettlebell swings and 10 burpees. Completed 4 rounds.",
    height=100
)

# 3. The Action Button
if st.button("Complete Quest"):
    if not workout_input:
        st.warning("Please enter a workout first!")
    else:
        # Show a loading spinner while the AI agents run
        with st.spinner("The Dungeon Master is reviewing your logs..."):
            try:
                # 4. Hit your local FastAPI backend
                response = requests.post(
                    "https://questfit-backend.onrender.com/",
                    data={"text_log": workout_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("is_valid_workout"):
                        st.success("Quest Successfully Logged!")
                        
                        # THE CREATIVE FLEX: Show the epic narrative prominently
                        st.markdown("### 📜 The Dungeon Master Says:")
                        st.info(f"*{data.get('quest_narrative')}*")
                        
                        # THE TECHNICAL FLEX: Show the clean JSON for engineers
                        with st.expander("🛠️ View the Structured AI Extraction (Under the Hood)"):
                            st.json(data.get("exercises"))
                    else:
                        st.error("The Vision Agent flagged this as junk data. Please enter a real workout.")
                else:
                    st.error(f"Backend Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection Error: Make sure your FastAPI server (main.py) is running in another terminal tab!")
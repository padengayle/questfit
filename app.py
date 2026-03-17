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
                # 4. Hit your live Render backend
                response = requests.post(
                    "https://questfit-backend.onrender.com/process-workout",
                    data={"text_log": workout_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("is_valid_workout"):
                        st.success("Quest Successfully Logged!")
                        
                        # THE CREATIVE FLEX: Show the epic narrative prominently
                        st.markdown("### 📜 The Dungeon Master Says:")
                        st.info(f"*{data.get('quest_narrative')}*")
                        
                        st.divider()
                        
                        # THE UI FLEX: Build the Visual RPG Dashboard
                        st.subheader("🛡️ Live Player Stats")
                        
                        current_level = data.get("current_level", 1)
                        total_xp = data.get("total_xp", 0)
                        
                        # Calculate progress to the next level (500 XP per level)
                        xp_into_current_level = total_xp % 500
                        progress_percentage = xp_into_current_level / 500.0
                        
                        # Create three columns for a clean metric layout
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(label="Current Level", value=current_level)
                        with col2:
                            st.metric(label="Total Lifetime XP", value=total_xp)
                        with col3:
                            st.metric(label="XP to Next Level", value=f"{xp_into_current_level} / 500")
                            
                        # Inject a visual progress bar
                        st.progress(progress_percentage, text="Level Progress")

                        st.divider()

                        # THE TECHNICAL FLEX: Show the clean JSON for engineers
                        with st.expander("🛠️ View the Structured AI Extraction (Under the Hood)"):
                            st.json(data.get("exercises"))
                    else:
                        st.error("The Vision Agent flagged this as junk data. Please enter a real workout.")
                else:
                    st.error(f"Backend Error: {response.status_code} {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Connection Error: The frontend cannot reach the backend. Check your Render dashboard to ensure the server is running!")
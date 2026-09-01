import streamlit as st
import json
import os
from biometrics import get_bmi
from planner import FitnessPlanner

# Configuration
PROFILE_FILE = 'user_profile.json'

st.set_page_config(page_title="AI Fitness Coach", page_icon="🚀")

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_profile(profile):
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=4)

def main():
    st.title("🚀 AI Fitness Coach")
    st.markdown("### Your Personalised, Local AI Training Partner")

    # Sidebar for Profile Management
    st.sidebar.header("User Profile")

    profile = load_profile()

    # Profile creation/update form
    with st.sidebar.expander("Edit Profile", expanded=(profile is None)):
        sex = st.selectbox("Sex", ["male", "female"], index=0 if not profile else (0 if profile['sex'].lower() == 'male' else 1))
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=85.0 if not profile else profile['weight'])
        height = st.number_input("Height (cm)", min_value=1.0, max_value=300.0, value=180.0 if not profile else profile['height'])
        age = st.number_input("Age", min_value=1, max_value=120, value=18 if not profile else profile['age'])

        activity_options = ["sedentary", "light", "moderate", "active", "extra_active"]
        activity = st.selectbox("Activity Level", activity_options,
                                index=2 if not profile else activity_options.index(profile['activity'].lower()) if profile['activity'].lower() in activity_options else 2)

        goal_options = ["weight_loss", "maintenance", "muscle_gain"]
        goal = st.selectbox("Goal", goal_options,
                            index=2 if not profile else goal_options.index(profile['goal'].lower()) if profile['goal'].lower() in goal_options else 2)

        equip_options = ["None", "Gym", "Bar"]
        # Handle case-insensitivity for equipment
        current_equip = profile['equipment'] if profile else "None"
        try:
            equip_index = [o.lower() for o in equip_options].index(current_equip.lower())
        except ValueError:
            equip_index = 0

        equipment = st.selectbox("Equipment", equip_options, index=equip_index)

        if st.button("Save Profile"):
            new_profile = {
                "sex": sex.lower(), "weight": weight, "height": height, "age": age,
                "activity": activity.lower(), "goal": goal.lower(), "equipment": equipment
            }
            save_profile(new_profile)
            st.success("Profile Saved!")
            st.rerun()

    # Current Profile Display
    if profile:
        st.info(f"**Active Profile:** {profile['sex'].capitalize()}, {profile['weight']}kg, {profile['height']}cm | Goal: {profile['goal'].replace('_', ' ').capitalize()}")
    else:
        st.warning("Please save your profile in the sidebar to begin!")
        return

    # Planning Phase
    if st.button("Generate My AI Plan ⚡️"):
        with st.spinner("Consulting DeepSeek-Coder-V2..."):
            try:
                planner = FitnessPlanner('exercises.json')
                plan = planner.curate_plan(profile)

                # Layout for metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("BMR", f"{plan['metrics']['bmr']} kcal")
                col2.metric("TDEE", f"{plan['metrics']['tdee']} kcal")
                col3.metric("Target", f"{plan['metrics']['target_calories']} kcal")

                st.markdown(f"**Your BMI:** {get_bmi(profile['weight'], profile['height'])}")

                st.divider()

                st.subheader("🤖 AI Coach's Curated Plan")
                st.markdown(plan['coach_advice'])

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

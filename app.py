import json
import random
import os
from biometrics import BiometricsCalculator
from planner import FitnessPlanner

DATASET_FILE = 'curation_dataset.jsonl'

def get_user_input(prompt, type_func=str, options=None):
    while True:
        user_input = input(f"{prompt}: ").strip()
        if not user_input:
            print("This field is required. Please enter a value.")
            continue

        if options and user_input.lower() not in [o.lower() for o in options]:
            print(f"Invalid option. Please choose from: {', '.join(options)}")
            continue

        try:
            return type_func(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {type_func.__name__}.")

def create_profile():
    print("\n--- Create Your Fitness Profile ---")
    profile = {
        "sex": get_user_input("Sex (male/female)", options=["male", "female"]).lower(),
        "weight": get_user_input("Weight (kg)", float),
        "height": get_user_input("Height (cm)", float),
        "age": get_user_input("Age", int),
        "activity": get_user_input("Activity Level (sedentary, light, moderate, active, extra_active)",
                                  options=["sedentary", "light", "moderate", "active", "extra_active"]).lower(),
        "goal": get_user_input("Goal (weight_loss, maintenance, muscle_gain)",
                               options=["weight_loss", "maintenance", "muscle_gain"]).lower(),
        "equipment": get_user_input("Equipment (None, Gym, Bar)", options=["None", "Gym", "Bar"])
    }

    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=4)

    print("\nProfile saved successfully!")
    return profile

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

def main():
    print("\n" + "="*50)
    print("🚀 AI FITNESS PROTOTYPE - DIRECT LINE ACTIVE")
    print("="*50)

    profile = load_profile()

    if profile:
        print("\nWelcome back!")
        print(f"Current Profile: {profile['sex']}, {profile['weight']}kg, {profile['height']}cm, Goal: {profile['goal']}")
        choice = input("\nWould you like to (1) Use this profile or (2) Update it? [1/2]: ").strip()
        if choice == '2':
            profile = create_profile()
    else:
        profile = create_profile()

    print("\n" + "="*50)
    print(f"User: {profile['sex']}, {profile['weight']}kg, {profile['height']}cm")
    print(f"Goal: {profile['goal']} | BMI: {get_bmi(profile['weight'], profile['height'])}")
    print("="*50 + "\n")

    try:
        planner = FitnessPlanner('exercises.json')
        plan = planner.curate_plan(profile)

        print("📊 NUTRITIONAL TARGETS")
        print(f"BMR: {plan['metrics']['bmr']} kcal")
        print(f"TDEE: {plan['metrics']['tdee']} kcal")
        print(f"Target: {plan['metrics']['target_calories']} kcal")
        print("-" * 30)

        print("\n🤖 AI COACH'S CURATED PLAN")
        print(plan['coach_advice'])
        print("\n" + "="*50)

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()

import json
import requests
import random
import os
from biometrics import BiometricsCalculator
from planner import FitnessPlanner

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" 
DATASET_FILE = 'curation_dataset.jsonl'
GUIDELINES_FILE = 'guidelines.txt'

def load_guidelines():
    """Loads the learned rules from the guidelines file."""
    if os.path.exists(GUIDELINES_FILE):
        with open(GUIDELINES_FILE, 'r') as f:
            return f.read().strip()
    return "No specific guidelines yet."

def save_guideline(rule):
    """Appends a new learned rule to the guidelines file."""
    with open(GUIDELINES_FILE, 'a') as f:
        f.write(f"\n- {rule}")

def get_random_profile():
    """Generates a random user profile."""
    activities = ["sedentary", "light", "moderate", "active", "extra_active"]
    goals = ["weight_loss", "maintenance", "muscle_gain"]
    equipment = ["None", "Gym", "Bar"]
    
    return {
        "sex": random.choice(["male", "female"]),
        "weight": round(random.uniform(50, 120), 1),
        "height": round(random.uniform(150, 200), 1),
        "age": random.randint(18, 65),
        "activity": random.choice(activities),
        "goal": random.choice(goals),
        "equipment": random.choice(equipment)
    }

def ask_llama(prompt):
    """Sends a prompt to the local Llama 3 model."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get('response', "No response from AI.")
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def main():
    print("\n" + "="*60)
    print("🌟 AI FITNESS GOLD-DATA CURATOR (LOOP-EDIT MODE) 🌟")
    print("="*60)
    print("Welcome, Coach. You can now polish plans infinitely until they are perfect.")
    print("Type 'quit' at any time to stop.\n")

    planner = FitnessPlanner('exercises.json')
    count = 0

    while True:
        # 1. Setup for a new profile
        current_rules = load_guidelines()
        profile = get_random_profile()
        
        print(f"\n--- NEW PROFILE ---")
        print(f"User: {profile['sex']}, {profile['weight']}kg, {profile['height']}cm, {profile['age']}yo")
        print(f"Goal: {profile['goal']} | Equipment: {profile['equipment']}")
        print("-" * 30)

        plan_data = planner.curate_plan(profile)
        
        # Generate the first draft
        prompt = f"""
        You are a world-class fitness coach. Create a professional, motivating, and detailed 7-day fitness plan.
        
        CURRENT COACHING GUIDELINES:
        {current_rules}
        
        USER: {profile['sex']}, {profile['age']}yo, {profile['weight']}kg, {profile['height']}cm.
        GOAL: {profile['goal']}. 
        TARGET CALORIES: {plan_data['metrics']['target_calories']} kcal.
        AVAILABLE EXERCISES: {json.dumps(plan_data['recommended_exercises'])}
        
        Provide a structured day-by-day plan with sets, reps, and a 'Why' for each day.
        """
        
        current_plan = ask_llama(prompt)

        # 2. THE POLISHING LOOP
        while True:
            print("\n🤖 CURRENT PLAN VERSION:")
            print("-" * 30)
            print(current_plan)
            print("-" * 30)

            print("\nACTION: [S] Save as Gold | [E] Edit/Critique | [N] Next Profile | [Q] Quit")
            action = input("Your choice: ").strip().lower()

            if action == 'q':
                print("Quitting...")
                return # Exit entire program
            
            elif action == 'n':
                print("Skipping this profile...")
                break # Break inner loop to get a new profile
            
            elif action == 's':
                save_example(profile, current_plan)
                count += 1
                print("\n✅ Example saved to Gold Dataset!")
                break # Break inner loop to get a new profile
            
            elif action == 'e':
                critique = input("\nWhat needs to be changed? (Be specific): ")
                
                # A. Refine the plan based on critique
                refine_prompt = f"Original Plan: {current_plan}\n\nCoach's Critique: {critique}\n\nRewrite the plan to be perfect based on this critique. Keep the structure professional."
                print("\nRefining plan...")
                current_plan = ask_llama(refine_prompt)
                
                # B. Learn the general rule from the critique
                print("\n🧠 Learning from your feedback...")
                rule_prompt = f"The AI wrote a plan, and the human coach corrected it with this feedback: '{critique}'.\n\nWhat is the general, concise fitness rule we should learn from this to avoid this mistake in the future? Write only the rule, no intro."
                new_rule = ask_llama(rule_prompt)
                save_guideline(new_rule)
                print(f"✅ Learned new rule: {new_rule}")
                
                print("\nPlan updated. Review it below.")
                # The loop continues, showing the new current_plan
            else:
                print("Invalid choice.")

    print(f"\nSession complete! You curated {count} Gold Standard examples.")

def save_example(profile, plan):
    example = {
        "instruction": f"Create a fitness plan for a {profile['sex']}, {profile['age']}yo, {profile['weight']}kg, {profile['height']}cm with goal {profile['goal']} and equipment {profile['equipment']}",
        "output": plan
    }
    with open(DATASET_FILE, 'a') as f:
        f.write(json.dumps(example) + "\n")

if __name__ == "__main__":
    main()
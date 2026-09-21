import json
import requests
from biometrics import BiometricsCalculator

class FitnessPlanner:
    def __init__(self, exercises_path, model_name="deepseek-coder-v2"):
        with open(exercises_path, 'r') as f:
            self.exercises = json.load(f)

        # Ollama API Configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = model_name

    def _get_ai_coach_advice(self, metrics, exercises, user_data):
        """
        Sends the calculated metrics and filtered exercises to Ollama
        to get a curated, human-sounding fitness plan.
        """
        prompt = f"""
        You are a world-class fitness coach. Create a professional, motivating, and detailed fitness plan.

        USER PROFILE:
        - Sex: {user_data['sex']}
        - Age: {user_data['age']}
        - Goal: {user_data['goal']}
        - Equipment: {user_data['equipment']}

        BIOMETRICS:
        - BMR: {metrics['bmr']} kcal
        - TDEE: {metrics['tdee']} kcal
        - Daily Target: {metrics['target_calories']} kcal

        AVAILABLE EXERCISES:
        {json.dumps(exercises, indent=2)}

        TASK:
        1. Create a 7-day workout schedule.
        2. For each day, pick the best exercises from the available list.
        3. Explain WHY these exercises and calories were chosen based on the user's goal.
        4. Provide clear instructions for sets, reps, and recovery.

        Be professional, encouraging, and scientifically accurate.
        """

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('response', "The AI coach is currently unavailable.")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def curate_plan(self, user_data):
        # 1. Calculate the numbers (The Science)
        bmr = BiometricsCalculator.calculate_bmr(
            user_data['weight'], user_data['height'], user_data['age'], user_data['sex']
        )
        tdee = BiometricsCalculator.calculate_tdee(bmr, user_data['activity'])
        target_calories = BiometricsCalculator.calculate_target_calories(tdee, user_data['goal'])

        metrics = {
            "bmr": round(bmr, 2),
            "tdee": round(tdee, 2),
            "target_calories": round(target_calories, 2)
        }

        # 2. Filter exercises (The Logic)
        available_equipment = user_data.get('equipment', 'None')
        curated_exercises = [ex for ex in self.exercises if ex['equipment'] == available_equipment or ex['equipment'] == 'None']

        # 3. Get the AI's curation (The "Coach" Layer)
        coach_advice = self._get_ai_coach_advice(metrics, curated_exercises, user_data)

        return {
            "metrics": metrics,
            "recommended_exercises": curated_exercises,
            "coach_advice": coach_advice
        }

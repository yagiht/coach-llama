class BiometricsCalculator:
    """
    Handles all biological calculations for fitness planning.
    Uses the Mifflin-St Jeor Equation for BMR.
    """

    ACTIVITY_FACTORS = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "extra_active": 1.9
    }

    @staticmethod
    def calculate_bmr(weight_kg, height_cm, age, sex):
        if sex.lower() == "male":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    @classmethod
    def calculate_tdee(cls, bmr, activity_level):
        factor = cls.ACTIVITY_FACTORS.get(activity_level.lower(), 1.2)
        return bmr * factor

    @staticmethod
    def calculate_target_calories(tdee, goal):
        goal_modifiers = {
            "weight_loss": -500,
            "maintenance": 0,
            "muscle_gain": 300
        }
        return tdee + goal_modifiers.get(goal.lower(), 0)

def get_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

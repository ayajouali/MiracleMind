# strategy.py
def generate_study_strategy(emotion_label, emotion_score, overloaded_score, performance_avg, concept_difficulty):
    """
    Renvoie une dict contenant durée de session (minutes), pause_every (minutes), conseils textuels.
    """
    if performance_avg is None:
        performance_avg = 0.6

    # Session duration
    base = 30
    duration = int(base * (0.5 + performance_avg))
    duration = max(10, min(90, duration))
    duration = int(duration * (1.0 - 0.5 * overloaded_score))

    # Break frequency
    if overloaded_score > 0.6 or emotion_label in ["sadness", "fear", "anger", "disgust"]:
        break_every = 5
        advice = "Commence par de courtes sessions et des tâches simples. Respire entre chaque session."
    elif emotion_label in ["joy", "surprise"] and performance_avg >= 0.7:
        break_every = 20
        advice = "Tu es en bonne forme : travaille par sessions plus longues et défis progressifs."
    else:
        break_every = 10
        advice = "Alterne révisions et exercices. Prends des pauses régulières."

    # Adjust for difficulty
    if concept_difficulty >= 4:
        duration = int(duration * 0.8)
        advice += " Pour ce concept difficile, divise la session en petites étapes."

    return {
        "session_duration_min": duration,
        "break_every_min": break_every,
        "advice": advice
    }
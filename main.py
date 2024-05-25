from flask import Flask, render_template, request, redirect, url_for, jsonify
import matplotlib.pyplot as plt
import numpy as np
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set Matplotlib to use the 'Agg' backend
plt.switch_backend('Agg')

# Predefined set of questions
QUESTIONS = [
        # social 1 - 4
    {"id": "eye_contact", "text": "Child avoids eye contact"},
    {"id": "response_to_name", "text": "Does not respond when their name is called"},
    {"id": "uses_gestures", "text": "Uses gestures to communicate"},
    {"id": "play_behavior", "text": "Prefer to play alone"},
        # behavior 5
    {"id": "follows_direction", "text": "Struggles following sequential steps"},
    {"id": "repetitive_behaviors", "text": "Repetitive behaviors (rocking, spinning, hand-flapping)"},
    {"id": "routines_or_rituals", "text": "Insistent on sticking to certain routines or rituals"},
    {"id": "intense_interests", "text": "Has intense interests in specific subjects or activities"},
        #emotion
    {"id": "handles_frustration", "text": "Unable to control frustration"},
    {"id": "shows_empathy", "text": "Lacks empathy towards others?"},
    {"id": "calming_strategies", "text": "Unable to calm themselves down"},
    {"id": "emotional_responses", "text": "Has inappropriate or exaggerated emotional responses to situations"},
        # Language
    {"id": "age_started_speaking", "text": "Delay or absence of typical developmental speech milestones"},
    {"id": "uses_language", "text": "Using language not typical for their age"},
    {"id": "imaginative_play", "text": "Engages in imaginative play?"},
    {"id": "unusual_speech_patterns", "text": "Uses repetitive or atypical speech patterns"},
        #sensory
    {"id": "unusual_reactions", "text": "Has unusual reactions to sensory experiences"},
    {"id": "clothing_textures_intolerance", "text": "Shows intolerance to certain clothing textures"},
    {"id": "seeks_sensory_experiences", "text": "Seeks sensory experiences"},
    {"id": "distress_noise_light", "text": "Shows distress or discomfort in response to specific noises or lights"},

]

@app.route("/questionnaire", methods=['GET', 'POST'])
def questionnaire():
    if request.method == 'POST':
        # Collect scores from the questionnaire using the defined questions
        scores = [int(request.form[question['id']]) for question in QUESTIONS]
        total_score = sum(scores)

        # Redirect to result page with scores as parameters
        return redirect(url_for('result', scores=','.join(map(str, scores))))

    return render_template("questions.html", questions=QUESTIONS)



@app.route("/result")
def result():
    scores_str = request.args.get('scores', '')
    if not scores_str:
        return "No scores provided", 400

    try:
        scores = list(map(int, scores_str.split(',')))
    except ValueError:
        return "Invalid scores format", 400

    if len(scores) != len(QUESTIONS):
        return "Incorrect number of scores", 400

    # Generate graphs
    try:
        generate_graphs(scores)
    except Exception as e:
        app.logger.error(f"Failed to generate graphs: {e}")
        return "Error generating graphs", 500

    # Calculate the total score from the assessment
    total_score = sum(scores)

    # Determine likelihood based on the score
    likelihood = "Low likelihood of ASD"
    if total_score > 60:  # Assuming a maximum score of 105
        likelihood = "High likelihood of ASD"
    elif total_score > 40:
        likelihood = "Moderate likelihood of ASD"

    # Calculate total scores for each category
    categories = ['social', 'behavior', 'language', 'sense', 'emotion']
    category_scores = {
        'social': sum([scores[i] for i in [0, 1, 2, 3]]),
        'behavior': sum([scores[i] for i in [4, 5, 6, 7]]),
        'emotion': sum([scores[i] for i in [8, 9, 10, 11]]),
        'language': sum([scores[i] for i in [12, 13, 14, 15]]),
        'sense': sum([scores[i] for i in [16, 17, 18, 19]]),
    }

    # Find the category with the highest score
    most_severe_area = max(category_scores, key=category_scores.get)

    return render_template("result.html", score=total_score, likelihood=likelihood, scores=scores, most_severe_area=most_severe_area)


def generate_graphs(scores):
    # Ensure the static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    # Bar Chart
    questions = [question['text'] for question in QUESTIONS]

    plt.figure(figsize=(10, 6))
    plt.barh(questions, scores, color='skyblue')
    plt.xlabel('Score')
    plt.ylabel('Questions')
    plt.title('Scores for Each Question')
    plt.tight_layout()
    plt.savefig('static/bar_chart.png')

    # Pie Chart
    categories = ['Social & Communication', 'Behavioral Patterns', 'Language Development', 'Sensory Sensitivity', 'Emotional Regulation']

    # Extract scores for each category
    social_communication_scores = [scores[i] for i in [0, 1, 2, 3]]
    behavioral_patterns_scores = [scores[i] for i in [4, 5, 6, 7]]
    emotional_regulation_scores = [scores[i] for i in [8, 9, 10, 11]]
    language_development_scores = [scores[i] for i in [12, 13, 14, 15]]
    sensory_sensitivity_scores = [scores[i] for i in [16, 17, 18, 19]]


    # Calculate total scores for each category
    category_scores = [
        sum(social_communication_scores),
        sum(behavioral_patterns_scores),
        sum(language_development_scores),
        sum(sensory_sensitivity_scores),
        sum(emotional_regulation_scores)
    ]




    # Radar Chart
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    radar_scores = category_scores + category_scores[:1]  # Repeat the first value to close the circle
    ax.fill(angles, radar_scores, color='skyblue', alpha=0.5)
    ax.plot(angles, radar_scores, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title('Radar Chart of Assessment Scores', size=20, color='blue', y=1.1)
    plt.tight_layout()
    plt.savefig('static/radar_chart.png')


@app.route("/language", methods=['GET', 'POST'])
def language():
    return render_template("language.html")

@app.route("/behavior", methods=['GET', 'POST'])
def behavior():
    return render_template("behavior.html")

@app.route("/emotion", methods=['GET', 'POST'])
def emotion():
    return render_template("emo.html")

@app.route("/sense", methods=['GET', 'POST'])
def sense():
    return render_template("sense.html")

@app.route("/social", methods=['GET', 'POST'])
def social():
    return render_template("social.html")

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

# Error handler for internal server errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')  # Run the Flask development server

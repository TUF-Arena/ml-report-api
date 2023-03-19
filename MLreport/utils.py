from statsmodels.stats.proportion import proportion_confint
from dotenv import dotenv_values
import os
import openai

def call_openai(message):
    config = dotenv_values(".env")
    openai.api_key = config["OPENAI_API_KEY"]
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user", 
                "content": message,
            }
        ]
    ).choices[0].message.content

def calculate_confidence(topic_scores):
    topic_confidence = {}
    for topic, scores in topic_scores.items():
        lower, upper = proportion_confint(scores[0], scores[1], alpha=0.05, method='agresti_coull')
        topic_confidence[topic] = [lower, upper]
    topic_confidence = sorted(topic_confidence.items(), key=lambda x: x[1])
    return topic_confidence

def get_recommendations(topic_confidence, limit=5):
    recommendations = []
    current_index = 0
    for topic, confidence in topic_confidence:
        if current_index == limit:
            break
        recommendations.append({
            "topic": topic,
            "recommendation": call_openai(
                f"You are helping someone as a data structures instructor, speak directly to them, they have a skill range of {confidence} in the topic {topic}, within 2 short sentences explain to them how they should furthur improve from their current skill level and suggest a few practice problems on leetcode, the difficulty of the suggested problems should align with the skill level of the user, do not mention the skill level of the student in your response, and just write one paragraph don't use new lines."
            )
        })
        current_index += 1
    return recommendations
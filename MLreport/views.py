from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from . import utils
import json

@api_view(['GET'])
def generate_report(request):
    data = {
        'Math': [2, 3],
        'Linked List': [1, 3],
        'Graph': [2, 7],	
        'Stacks': [0, 1],
        'Dynamic Programming': [4, 5],
        'Arrays': [10, 10],
        'Strings': [100, 100],
		}
    topic_confidence = utils.calculate_confidence(data)
    recommendations = utils.get_recommendations(topic_confidence)	
    return Response({
        'topic_confidence': topic_confidence,
        'recommendations': recommendations
    }, status=status.HTTP_200_OK)
from rest_framework.decorators import api_view
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import matplotlib
from . import utils
import textwrap
import random
import numpy
import io

matplotlib.use('agg')

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

    buffer = io.BytesIO()
    canvas_object = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    text_object = canvas_object.beginText()
    text_object.setTextOrigin(inch, inch)
    text_object.setFont('Helvetica', 12)
    text_object.textLine("Your Report")
    for i in range(0, 15):
        text_object.textLine("")

    topics=[]
    lower=[]
    upper=[]
    for topic, scores in topic_confidence:
        lower.append(scores[0])
        upper.append(scores[1])
        topics.append(topic)

    fig = plt.figure(figsize=(16, 9), dpi=200)
    plt.hist([topics, topics], bins=len(topics), alpha=0.5,
            label=['lower confidence', 'upper confidence'], weights=[lower, upper], color=['red', 'green'])
    plt.xticks(range(len(topics)), topics)
    plt.legend(loc='upper right', fontsize=20)

    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png', dpi=200)
    imgdata.seek(0)
    Image = ImageReader(imgdata)
    canvas_object.drawImage(Image, 0, 75, 600, 200)

    for recommendation in recommendations:
        text_object.textLine(f"{recommendation['topic']}:")
        lines = textwrap.wrap(recommendation['recommendation'], width=int(1000/text_object._fontsize))
        for line in lines:
            padded_line = "{:<{width}}".format(line, width=int(1000/text_object._fontsize))
            text_object.textLine(padded_line)
        text_object.textLine("")

    canvas_object.drawText(text_object)
    canvas_object.showPage()
    canvas_object.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='your-report.pdf')
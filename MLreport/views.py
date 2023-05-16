from rest_framework.decorators import api_view
from django.http import FileResponse, JsonResponse
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

def generate_pdf(data):
    buffer = io.BytesIO()
    canvas_object = canvas.Canvas(buffer)
    canvas_object.setFont("Helvetica", 12)
    x = 50
    y = 700
    for key, value in data.items():
        canvas_object.drawString(x, y, f"{key}:")
        lines = value.split("\n")
        for line in lines:
            canvas_object.drawString(x + 20, y, line)
            y -= 20
            if y <= 50:
                canvas_object.showPage()
                y = 800
        y -= 20
    canvas_object.save()
    buffer.seek(0)
    return buffer


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

    return FileResponse(buffer, as_attachment=True, filename='topic-performance-report.pdf')

@api_view(['GET'])
def code_quality(request):
    data = {
        'source_code': 
        """
        #define mod 1000000007
        typedef long long ll;

        class Solution {
        public:
            int sumOfPower(vector<int>& nums) {
                sort(nums.begin(), nums.end());
                ll n = nums.size();
                ll prefix = 0LL;
                ll ans = 0LL;
                for (ll i = 0LL; i < n; i ++) {
                    ll single = (((ll)nums[i] % mod * (ll)nums[i] % mod) % mod * (ll)nums[i] % mod) % mod;
                    ll other = (((ll)prefix % mod * (ll)nums[i] % mod) % mod * (ll)nums[i] % mod) % mod;
                    ans = ((ll)ans % mod + ((ll)other % mod + (ll)single % mod) % mod) % mod;
                    prefix = ((ll)prefix * 2LL + (ll)nums[i]) % mod;
                }
                return ans % mod;
            }
        };
        """
	}

    code_quality_response = utils.get_code_quality_data(data['source_code'])
    buffer = generate_pdf(code_quality_response)
    return FileResponse(buffer, as_attachment=True, filename='code-quality-report.pdf')

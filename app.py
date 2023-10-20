from flask import Flask, render_template, request, url_for, send_from_directory
import os
import PyPDF2
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
import base64
from PyPDF2 import PdfReader
import numpy as np
import logging
from flask import Flask, request, redirect, url_for, flash, render_template


logging.getLogger("matplotlib").setLevel(logging.WARNING)

matplotlib.use("Agg")  # Set backend to Agg
app = Flask(__name__)
app.secret_key = "your_secret_key_here"


# ESG positive words
E_WORDS = set(
    ["environment", "green", "sustainable", "renewable", ...]
)  # Add any other 'E' related words you have in mind
S_WORDS = set(
    ["social", "inclusive", "equality", ...]
)  # ... and so on for 'S' and 'G' words
G_WORDS = set(["governance", "ethics", "transparent", ...])

# ESG negative words
E_NEG_WORDS = set(
    ["pollution", "waste", "emission", ...]
)  # Add any negative 'E' related words you have in mind
S_NEG_WORDS = set(
    ["discrimination", "inequality", ...]
)  # ... and so on for negative 'S' and 'G' words
G_NEG_WORDS = set(["corruption", "fraud", ...])


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching


def analyze_pdf(data):
    with io.BytesIO(data) as f:
        reader = PdfReader(f)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()

    words = text.split()
    e_count = sum(word.lower() in E_WORDS for word in words)
    s_count = sum(word.lower() in S_WORDS for word in words)
    g_count = sum(word.lower() in G_WORDS for word in words)

    # Create Bar Chart
    labels = ["E", "S", "G"]
    positive_counts = [e_count, s_count, g_count]
    negative_counts = ([word.lower() in E_NEG_WORDS for word in words].count(True),)
    [word.lower() in S_NEG_WORDS for word in words].count(True),
    [word.lower() in G_NEG_WORDS for word in words].count(True)
    barWidth = 0.3
    r1 = np.arange(len(positive_counts))
    r2 = [x + barWidth for x in r1]

    plt.bar(
        r1,
        positive_counts,
        color="blue",
        width=barWidth,
        edgecolor="grey",
        label="positive",
    )
    plt.bar(
        r2,
        negative_counts,
        color="red",
        width=barWidth,
        edgecolor="grey",
        label="negative",
    )

    plt.xlabel("Categories", fontweight="bold")
    plt.xticks([r + barWidth for r in range(len(positive_counts))], ["E", "S", "G"])
    plt.legend()

    # Convert Plot to Image String for Rendering
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)

    return {"E": e_count, "S": s_count, "G": g_count}, img.read()


# Quick function to validate file extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def upload_route():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file:
            # Analyze the uploaded PDF
            counts, img_data = analyze_pdf(file.read())

            # Log the results (this is optional)
            app.logger.info(
                f"Analysis Results: E:{counts['E']}, S:{counts['S']}, G:{counts['G']}"
            )

            # Return the results to be rendered on the web page
            return render_template(
                "upload.html",
                scores=counts,
                img_data=base64.b64encode(img_data).decode("utf-8"),
            )

    # This part handles the GET request which displays the initial upload page
    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)

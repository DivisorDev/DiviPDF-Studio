from flask import Flask, request, jsonify, send_file
from pdf2docx import Converter
from fpdf import FPDF
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import os
import io
import zipfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend from GitHub Pages to access this API

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return jsonify({"message": "DiviPDF Multi-Tool API is running successfully!"})

# ========== PDF TOOLS SECTION ==========

# 1️⃣ PDF → Word
@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word():
    try:
        file = request.files['file']
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        word_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0] + ".docx")

        cv = Converter(pdf_path)
        cv.convert(word_path)
        cv.close()

        return send_file(word_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2️⃣ Word → PDF
@app.route('/word-to-pdf', methods=['POST'])
def word_to_pdf():
    try:
        from docx import Document
        from reportlab.pdfgen import canvas

        file = request.files['file']
        word_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(word_path)

        pdf_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0] + ".pdf")

        doc = Document(word_path)
        c = canvas.Canvas(pdf_path)
        textobject = c.beginText(40, 800)
        for para in doc.paragraphs:
            textobject.textLine(para.text)
        c.drawText(textobject)
        c.save()

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3️⃣ Merge PDF
@app.route('/merge-pdf', methods=['POST'])
def merge_pdf():
    try:
        files = request.files.getlist('files')
        merger = PdfMerger()
        for f in files:
            pdf_path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(pdf_path)
            merger.append(pdf_path)

        output_path = os.path.join(OUTPUT_FOLDER, "merged.pdf")
        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 4️⃣ Compress PDF
@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    try:
        file = request.files['file']
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)

        output_path = os.path.join(OUTPUT_FOLDER, "compressed.pdf")
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========== IMAGE TOOLS SECTION ==========

# 1️⃣ Image Compressor (JPG/PNG/WebP)
@app.route('/compress-image', methods=['POST'])
def compress_image():
    try:
        file = request.files['file']
        img = Image.open(file.stream)
        output_path = os.path.join(OUTPUT_FOLDER, file.filename)
        img.save(output_path, optimize=True, quality=60)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2️⃣ Image Resize (Custom)
@app.route('/resize-image', methods=['POST'])
def resize_image():
    try:
        width = int(request.form['width'])
        height = int(request.form['height'])
        file = request.files['file']

        img = Image.open(file.stream)
        resized = img.resize((width, height))
        output_path = os.path.join(OUTPUT_FOLDER, "resized_" + file.filename)
        resized.save(output_path)

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3️⃣ Image → PDF
@app.route('/image-to-pdf', methods=['POST'])
def image_to_pdf():
    try:
        file = request.files['file']
        img = Image.open(file.stream).convert("RGB")
        output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0] + ".pdf")
        img.save(output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 4️⃣ Convert Image Format (JPG/PNG/WebP)
@app.route('/convert-image', methods=['POST'])
def convert_image():
    try:
        file = request.files['file']
        format = request.form['format'].upper()  # PNG/JPG/WEBP
        img = Image.open(file.stream)
        output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0] + f".{format.lower()}")
        img.save(output_path, format=format)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
import mammoth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
EDITS_FOLDER = os.path.join(BASE_DIR, "edits")
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EDITS_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"xlsx", "xls", "docx", "txt", "pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "troque_esta_chave_por_uma_variavel_de_ambiente_em_producao"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("Nenhum arquivo enviado.")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("Arquivo sem nome.")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            flash(f"Arquivo salvo: {filename}")
            return redirect(url_for("uploaded_file", filename=filename))
        else:
            flash("Tipo de arquivo não permitido.")
            return redirect(request.url)
    return render_template("upload.html")

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/generate_from_docx/<filename>")
def generate_from_docx(filename):
    # Exemplo simples: converte .docx para HTML e salva em edits/
    src = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(src) or not filename.lower().endswith(".docx"):
        flash("Arquivo .docx não encontrado.")
        return redirect(url_for("index"))
    with open(src, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html = result.value
    out_name = secure_filename(filename.rsplit(".", 1)[0] + ".html")
    out_path = os.path.join(EDITS_FOLDER, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    flash(f"HTML gerado: {out_name}")
    return send_from_directory(EDITS_FOLDER, out_name, as_attachment=True)

@app.route("/list_uploads")
def list_uploads():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("files_list.html", files=files)

if __name__ == "__main__":
    app.run(debug=True)
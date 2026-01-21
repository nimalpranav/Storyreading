from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# ===============================
# CONFIG
# ===============================
UPLOAD_FOLDER = 'uploads'
ADS_FOLDER = 'ads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ADS_FOLDER, exist_ok=True)

# ===============================
# HOME PAGE
# ===============================
@app.route('/')
def home():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]
    ads = os.listdir(ADS_FOLDER)

    if not files:
        return """
        <h1 style="color:white;background:black;height:100vh;
        display:flex;align-items:center;justify-content:center;">
        No stories found in uploads folder
        </h1>
        """

    pdf = files[0]
    ad = ads[0] if ads else ''
    return redirect(url_for('read', pdf=pdf, ad=ad))

# ===============================
# READER PAGE
# ===============================
@app.route('/read')
def read():
    pdf = request.args.get('pdf')
    ad = request.args.get('ad')
    return render_template_string(READER_HTML, pdf=pdf, ad=ad)

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/ads/<path:filename>')
def ads(filename):
    return send_from_directory(ADS_FOLDER, filename)

# ===============================
# HTML TEMPLATE
# ===============================
READER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Story Reader</title>

<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<style>
.page {
  transition: transform 0.6s;
}
.flip {
  transform: rotateY(-180deg);
}
#adBox {
  position: fixed;
  top: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.9);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
</style>
</head>

<body class="bg-black text-white overflow-hidden">

<div id="adBox">
  <img id="adImage" class="max-h-[80vh] rounded-3xl shadow-2xl">
</div>

<div class="flex items-center justify-center h-screen">
  <button onclick="prevPage()" class="text-5xl px-4">⬅</button>
  <canvas id="pdf" class="page rounded-2xl shadow-2xl"></canvas>
  <button onclick="nextPage()" class="text-5xl px-4">➡</button>
</div>

<script>
// ===============================
// FULLSCREEN
// ===============================
function goFullScreen() {
  const el = document.documentElement;
  if (el.requestFullscreen) el.requestFullscreen();
}
setTimeout(goFullScreen, 500);

// ===============================
// PDF
// ===============================
const url = '/uploads/{{ pdf }}';
let pdfDoc = null;
let pageNum = 1;

pdfjsLib.getDocument(url).promise.then(doc => {
  pdfDoc = doc;
  renderPage();
});

function renderPage() {
  pdfDoc.getPage(pageNum).then(page => {
    const canvas = document.getElementById('pdf');
    const ctx = canvas.getContext('2d');
    const viewport = page.getViewport({ scale: 1.5 });
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    page.render({ canvasContext: ctx, viewport: viewport });
  });
}

function nextPage() {
  if (pageNum < pdfDoc.numPages) {
    pageNum++;
    flip();
  }
}

function prevPage() {
  if (pageNum > 1) {
    pageNum--;
    flip();
  }
}

function flip() {
  const canvas = document.getElementById('pdf');
  canvas.classList.add('flip');
  setTimeout(() => {
    renderPage();
    canvas.classList.remove('flip');
  }, 300);
}

// ===============================
// RANDOM ADS
// ===============================
const adBox = document.getElementById("adBox");
const adImage = document.getElementById("adImage");

const ads = [
  "/ads/{{ ad }}",
  "/ads/ad1.jpg",
  "/ads/ad2.jpg",
  "/ads/ad3.jpg"
];

function showAd() {
  const randomAd = ads[Math.floor(Math.random() * ads.length)];
  adImage.src = randomAd;
  adBox.style.display = "flex";

  setTimeout(() => {
    adBox.style.display = "none";
  }, 5000);
}

setTimeout(showAd, 3000);      // show once
setInterval(showAd, 300000);  // every 5 min
</script>

</body>
</html>
"""

# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    app.run(debug=True)
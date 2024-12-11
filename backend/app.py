import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

s3 = boto3.client("s3")

BUCKET_NAME = "pgo-id-scanning-bucket-1o3ky4jp"


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"message": "Wating for files to upload!"})


@app.route("/api/uploadfile", methods=["POST"])
def upload_s3():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
        img.save(f"./{filename}")
        try:
            s3.upload_file(Bucket=BUCKET_NAME, Filename=filename, Key=filename)
        except Exception as ex:
            return jsonify({"message": "Error", "error": str(ex.text)})

    return jsonify({"message": "OK"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

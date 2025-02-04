import inspect
import json
import logging
import os
import sys
from datetime import datetime

import amaas.grpc
import boto3
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

_LOGGER = logging.getLogger()
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s (%(threadName)s) [%(funcName)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = Flask(__name__)
CORS(app)

s3 = boto3.client("s3")

BUCKET_NAME = os.getenv("BUCKET_NAME")
if BUCKET_NAME == "":
    BUCKET_NAME = None

V1_REGION = os.getenv("V1_REGION")
if V1_REGION == "" or V1_REGION is None:
    V1_REGION = "us-east-1"
V1_API_KEY = os.getenv("V1_API_KEY")
if V1_REGION == "us-east-1":
    API_BASE_URL = "https://api.xdr.trendmicro.com"
else:
    API_BASE_URL = f"https://api.{V1_REGION}.xdr.trendmicro.com"

# FSS
FSS_TAG_PREFIX = "filesecurity-"
FSS_PML = True
FSS_FEEDBACK = True
FSS_VERBOSE = True
FSS_DIGEST = True
# /FSS

# SANDBOX
SB_TAG_PREFIX = "sandbox-"
URL_PATH_ANALYZE = "/v3.0/sandbox/files/analyze"
URL_PATH_TASKS = "/v3.0/sandbox/tasks"
HEADERS = {"Authorization": "Bearer " + V1_API_KEY}
QUERY_PARAMS = {}
SANDBOX_FORWARD = [
    7,    # VSDT_EXE
    28,   # VSDT_TEXT
    19,   # VSDT_ELF
    4,    # VSDT_EXCELL
    2,    # VSDT_PPT
    30,   # VSDT_PROJECT
    1,    # VSDT_WINWORD
    4045, # VSDT_OFFICE12
    1003, # VSDT_OFFICEXML
    4049, # VSDT_JAR
    6015, # VSDT_PDF
]
# /SANDBOX


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"message": "Let me crunch your files for you!"})


@app.route("/api/uploadfile", methods=["POST"])
def upload_s3():
    img = request.files["file"]
    bucket = request.form.get("bucket")
    if bucket == "null":
        bucket = BUCKET_NAME
    if bucket is None:
        return jsonify({"error": "Choose an upload Bucket first!"})
    if img:
        filename = secure_filename(img.filename)
        _LOGGER.info(
            f"Sending {filename} to S3 Bucket",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        img.save(f"./{filename}")
        try:
            s3.upload_file(Bucket=bucket, Filename=filename, Key=filename)
        except Exception as ex:
            return jsonify({"error": str(ex)})

    return jsonify({"message": "OK"})


@app.route("/api/scansandbox", methods=["POST"])
def scan_sandbox():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
        _LOGGER.info(
            f"Sending {filename} to Sandbox",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        try:
            task_id = sandbox_submit(key=filename, buffer=img.read())
        except Exception as ex:
            _LOGGER.error(str(ex))
            return jsonify({"error": str(ex)})

    _LOGGER.info(task_id, extra={"function": inspect.currentframe().f_code.co_name})
    return jsonify({"message": "OK", "task_id": task_id})


@app.route("/api/scansandbox/<id>", methods=["GET"])
def scan_sandbox_status(id):
    _LOGGER.info(
        f"Query Task ID {id} from Sandbox",
        extra={"function": inspect.currentframe().f_code.co_name},
    )
    try:
        sandbox_analysis_results = sandbox_task_status(id)
    except Exception as ex:
        _LOGGER.error(str(ex))
        return jsonify({"error": str(ex)})

    _LOGGER.info(
        sandbox_analysis_results,
        extra={"function": inspect.currentframe().f_code.co_name},
    )
    return jsonify(
        {
            "message": f"Sandbox Scan {sandbox_analysis_results.get('status')}",
            "status": sandbox_analysis_results.get("status"),
            "response": sandbox_analysis_results,
            "resourceLocation": sandbox_analysis_results.get("resourceLocation"),
        }
    )


@app.route("/api/resultsandbox/", methods=["POST"])
def scan_sandbox_result():
    if request.form.get("resourceLocation") != "undefined":
        resourceLocation = request.form.get("resourceLocation")
    else:
        resourceLocation = None
    sandbox_analysis_results = {
        "resourceLocation": resourceLocation,
        "lastActionDateTime": request.form.get("lastActionDateTime"),
        "error": {
            "code": request.form.get("errorCode"),
            "message": request.form.get("errorMessage"),
        },
    }
    _LOGGER.info(
        f"Query Result {request.form} from Sandbox",
        extra={"function": inspect.currentframe().f_code.co_name},
    )
    try:
        sandbox_analysis_results = sandbox_get_analysis_results(
            sandbox_analysis_results
        )
    except Exception as ex:
        _LOGGER.error(str(ex))
        return jsonify({"error": str(ex)})

    _LOGGER.info(
        sandbox_analysis_results,
        extra={"function": inspect.currentframe().f_code.co_name},
    )
    return jsonify({"message": "OK", "tags": sandbox_analysis_results})


@app.route("/api/scanfs", methods=["POST"])
def scan_fs():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
        _LOGGER.info(
            f"Sending {filename} to File Security",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        try:
            tags = fss_submit(key=filename, buffer=img.read())
            _LOGGER.info(
                tags, extra={"function": inspect.currentframe().f_code.co_name}
            )
        except Exception as ex:
            return jsonify({"error": str(ex)})

    _LOGGER.info(tags, extra={"function": inspect.currentframe().f_code.co_name})
    return jsonify({"message": "OK", "tags": tags})


@app.route("/api/scancs", methods=["POST"])
def scan_cs():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
        _LOGGER.info(
            f"Sending {filename} to Container",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        img.save(f"./{filename}")

    return jsonify({"message": "OK"})


@app.route("/api/listbuckets", methods=["GET"])
def list_buckets():
    buckets = []

    try:
        response = s3.list_buckets(
            MaxBuckets=100,
            # ContinuationToken='string',
            # Prefix='string',
            # BucketRegion='string'
        )

        for bucket in response.get("Buckets"):
            buckets.append({"value": bucket.get("Name"), "label": bucket.get("Name")})
    except Exception as ex:
        return jsonify({"error": str(ex)})

    return jsonify({"message": "OK", "buckets": buckets})


# #############################################################################
# File Security Handling
# #############################################################################
def fss_submit(key, buffer):
    handle = amaas.grpc.init_by_region(V1_REGION, V1_API_KEY, True)
    try:
        scan_resp = amaas.grpc.scan_buffer(
            handle,
            buffer,
            key,
            tags=["pgo"],
            pml=FSS_PML,
            feedback=FSS_FEEDBACK,
            verbose=FSS_VERBOSE,
            digest=FSS_DIGEST,
        )
    except Exception as e:
        _LOGGER.error(e, extra={"function": inspect.currentframe().f_code.co_name})
        _LOGGER.error(
            "Error scanning object {}.".format(key),
            extra={"function": inspect.currentframe().f_code.co_name},
        )

    response = json.loads(scan_resp)
    _LOGGER.info(response, extra={"function": inspect.currentframe().f_code.co_name})
    scanning_result = response.get("result")
    findings = scanning_result.get("atse").get("malwareCount")
    scan_result = "malicious" if findings else "no issues found"
    error = scanning_result.get("atse").get("error")
    if error is not None:
        scan_result = error
    scan_date = datetime.strftime(
        datetime.fromisoformat(response.get("timestamp").get("end")),
        "%m/%d/%Y %H:%M:%S",
    )
    malware_name = (
        scanning_result.get("atse").get("malware")[0].get("name") if findings else "n/a"
    )
    
    tags = [
        f"{FSS_TAG_PREFIX}scanned=true",
        f"{FSS_TAG_PREFIX}scan-date={scan_date}",
        f"{FSS_TAG_PREFIX}scan-result={scan_result}",
        f"{FSS_TAG_PREFIX}scan-detail-code={malware_name}",
    ]

    file_type = scanning_result.get("atse").get("fileType")
    if file_type in SANDBOX_FORWARD:
        tags.append("sandbox")
        
    amaas.grpc.quit(handle)

    _LOGGER.info(tags, extra={"function": inspect.currentframe().f_code.co_name})

    return tags


# #############################################################################
# Sandbox Handling
# #############################################################################
def sandbox_submit(key, buffer):
    data = {
        #    'documentPassword': 'YOUR_DOCUMENTPASSWORD (base64-encoded characters)',
        #    'archivePassword': 'YOUR_ARCHIVEPASSWORD (base64-encoded characters)',
        #    'arguments': 'YOUR_ARGUMENTS (base64-encoded characters)'
    }
    files = {"file": (key, buffer, "application/octet-stream")}
    try:
        response = requests.post(
            API_BASE_URL + URL_PATH_ANALYZE,
            params=QUERY_PARAMS,
            headers=HEADERS,
            data=data,
            files=files,
        )
        # response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        _LOGGER.error(
            errh.args[0], extra={"function": inspect.currentframe().f_code.co_name}
        )
        raise
    except requests.exceptions.ReadTimeout:
        _LOGGER.error(
            "Time out", extra={"function": inspect.currentframe().f_code.co_name}
        )
        raise
    except requests.exceptions.ConnectionError:
        _LOGGER.error(
            "Connection error",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        raise
    except requests.exceptions.RequestException:
        _LOGGER.error(
            "Exception request",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        raise

    task_id = response.json().get("id")

    _LOGGER.info(
        f"Sandbox Task ID: {task_id}",
        extra={"function": inspect.currentframe().f_code.co_name},
    )

    return task_id


def sandbox_task_status(task_id):
    try:
        response = requests.get(
            API_BASE_URL + URL_PATH_TASKS + "/" + task_id,
            params=QUERY_PARAMS,
            headers=HEADERS,
        )
        # response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        _LOGGER.error(
            errh.args[0], extra={"function": inspect.currentframe().f_code.co_name}
        )
        raise
    except requests.exceptions.ReadTimeout:
        _LOGGER.error(
            "Time out", extra={"function": inspect.currentframe().f_code.co_name}
        )
        raise
    except requests.exceptions.ConnectionError:
        _LOGGER.error(
            "Connection error",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        raise
    except requests.exceptions.RequestException:
        _LOGGER.error(
            "Exception request",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        raise

    task_result = response.json()
    _LOGGER.info(
        f"Sandbox Analysis {task_result.get("status")}",
        extra={"function": inspect.currentframe().f_code.co_name},
    )

    return task_result


def sandbox_get_analysis_results(sandbox_analysis_results):
    resource = sandbox_analysis_results.get("resourceLocation")
    if resource is not None:
        try:
            response = requests.get(
                sandbox_analysis_results.get("resourceLocation"),
                params=QUERY_PARAMS,
                headers=HEADERS,
            )
            # response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error(
                errh.args[0], extra={"function": inspect.currentframe().f_code.co_name}
            )
            raise
        except requests.exceptions.ReadTimeout:
            _LOGGER.error(
                "Time out", extra={"function": inspect.currentframe().f_code.co_name}
            )
            raise
        except requests.exceptions.ConnectionError:
            _LOGGER.error(
                "Connection error",
                extra={"function": inspect.currentframe().f_code.co_name},
            )
            raise
        except requests.exceptions.RequestException:
            _LOGGER.error(
                "Exception request",
                extra={"function": inspect.currentframe().f_code.co_name},
            )
            raise

        analysis_result = response.json()

        detection_names = " ".join(analysis_result.get("detectionNames", ["n/a"]))
        if detection_names == "":
            detection_names = "n/a"
        threat_types = " ".join(analysis_result.get("threatTypes", ["n/a"]))
        if threat_types == "":
            threat_types = "n/a"
        scan_date = datetime.strftime(
            datetime.fromisoformat(analysis_result.get("analysisCompletionDateTime")),
            "%m/%d/%Y %H:%M:%S",
        )
        tags = [
            f"{SB_TAG_PREFIX}risk-level={analysis_result.get('riskLevel', 'n/a')}",
            f"{SB_TAG_PREFIX}detection-names={detection_names}",
            f"{SB_TAG_PREFIX}threat-type={threat_types}",
            f"{SB_TAG_PREFIX}analysis-completed={scan_date}",
        ]
    else:
        last_action_date = datetime.strftime(
            datetime.fromisoformat(sandbox_analysis_results.get("lastActionDateTime")),
            "%m/%d/%Y %H:%M:%S",
        )
        tags = [
            f"{SB_TAG_PREFIX}code={sandbox_analysis_results.get('error').get('code', 'n/a')}",
            f"{SB_TAG_PREFIX}message={sandbox_analysis_results.get('error').get('message', 'n/a')}",
            f"{SB_TAG_PREFIX}analysis-completed={last_action_date}",
        ]
    _LOGGER.info(tags, extra={"function": inspect.currentframe().f_code.co_name})

    return tags


if __name__ == "__main__":
    _LOGGER.info(f"V1 Region: {V1_REGION}")
    _LOGGER.info(f"API Key: ...{V1_API_KEY[-4:]}")
    _LOGGER.info(f"API Base URL: {API_BASE_URL}")
    _LOGGER.info(f"Bucket Name: {BUCKET_NAME}")
    _LOGGER.info(f"AWS Access Key: {os.getenv('AWS_ACCESS_KEY_ID', '')}")
    _LOGGER.info(
        f"AWS Secret Key: {"".ljust(len(os.getenv('AWS_SECRET_ACCESS_KEY', '')), '*')}"
    )

    app.run(debug=True, host="0.0.0.0")

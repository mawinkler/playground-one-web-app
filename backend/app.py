import inspect
import json
import logging
import os
import sys
from datetime import datetime
from time import sleep

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
        try:
            task_id = sandbox_submit(key=filename, buffer=img.read())
            sandbox_analysis_results = sandbox_wait_for_result(task_id)
            tags = sandbox_get_analysis_results(sandbox_analysis_results)
        except Exception as ex:
            return jsonify({"error": str(ex)})

    return jsonify({"message": "OK", "tags": tags})


@app.route("/api/scanfs", methods=["POST"])
def scan_fs():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
        _LOGGER.info(filename)
        try:
            tags = fss_submit(key=filename, buffer=img.read())
            _LOGGER.info(tags)
        except Exception as ex:
            return jsonify({"error": str(ex)})

    return jsonify({"message": "OK", "tags": tags})


@app.route("/api/scancs", methods=["POST"])
def scan_cs():
    img = request.files["file"]
    if img:
        filename = secure_filename(img.filename)
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
    _LOGGER.info("FSS SCAN")
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

    scanning_result = response.get("result")
    _LOGGER.info(scanning_result)
    findings = scanning_result.get("atse").get("malwareCount")
    _LOGGER.info(findings)
    scan_result = "malicious" if findings else "no issues found"
    _LOGGER.info(scan_result)
    scan_date = datetime.strftime(
        datetime.fromisoformat(response.get("timestamp").get("end")),
        "%m/%d/%Y %H:%M:%S",
    )
    _LOGGER.info(scan_date)
    malware_name = (
        scanning_result.get("atse").get("malware")[0].get("name") if findings else "n/a"
    )
    _LOGGER.info(malware_name)

    tags = [
        f"{FSS_TAG_PREFIX}scanned=true",
        f"{FSS_TAG_PREFIX}scan-date={scan_date}",
        f"{FSS_TAG_PREFIX}scan-result={scan_result}",
        f"{FSS_TAG_PREFIX}scan-detail-code={malware_name}",
    ]

    amaas.grpc.quit(handle)

    _LOGGER.info(tags)

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
        response.raise_for_status()
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


def sandbox_wait_for_result(task_id):

    sandbox_analysis_results = None
    sandbox_analysis_failed = False
    while sandbox_analysis_results is None and not sandbox_analysis_failed:
        try:
            response = requests.get(
                API_BASE_URL + URL_PATH_TASKS + "/" + task_id,
                params=QUERY_PARAMS,
                headers=HEADERS,
            )
            response.raise_for_status()
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
        if task_result.get("status") == "succeeded":
            sandbox_analysis_results = task_result.get("resourceLocation")
        if task_result.get("status") == "failed":
            sandbox_analysis_failed = True
        _LOGGER.info(
            "Sandbox Analysis running",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        sleep(10)

    if sandbox_analysis_failed:
        _LOGGER.error(
            "Sandbox Analysis failed",
            extra={"function": inspect.currentframe().f_code.co_name},
        )
        raise Exception("Sandbox Analysis failed")

    return sandbox_analysis_results


def sandbox_get_analysis_results(sandbox_analysis_results):
    try:
        response = requests.get(
            sandbox_analysis_results, params=QUERY_PARAMS, headers=HEADERS
        )
        response.raise_for_status()
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
    threat_types = " ".join(analysis_result.get("threatTypes", ["n/a"]))
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

    _LOGGER.info(tags)

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

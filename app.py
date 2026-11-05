from flask import Flask, jsonify
from urllib.request import Request, urlopen

app = Flask(__name__)

METADATA_URL = "http://169.254.169.254/latest"


def get_metadata(path):
    # Request an IMDSv2 token
    token_request = Request(
        f"{METADATA_URL}/api/token",
        method="PUT",
        headers={
            "X-aws-ec2-metadata-token-ttl-seconds": "21600"
        }
    )

    with urlopen(token_request, timeout=2) as response:
        token = response.read().decode()

    # Use the token to retrieve instance metadata
    metadata_request = Request(
        f"{METADATA_URL}/meta-data/{path}",
        headers={
            "X-aws-ec2-metadata-token": token
        }
    )

    with urlopen(metadata_request, timeout=2) as response:
        return response.read().decode()


@app.route("/")
def home():
    return "AWS Instance Information API is running!"


@app.route("/metadata")
def metadata():
    try:
        region = get_metadata("placement/region")
        availability_zone = get_metadata("placement/availability-zone")

        return jsonify({
            "region": region,
            "availability_zone": availability_zone
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
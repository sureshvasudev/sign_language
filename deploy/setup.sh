#!/bin/bash
# AI Sign Language Translator: sets up the AWS server. upload.bat runs this for you.
# Safe to run again (for example after changing the code): it only redoes what is needed.
set -e

APP_FOLDER=/home/ubuntu/sign_language

# Read one setting (for example DOMAIN) from the settings file CloudFormation saved.
setting() {
  sudo grep "^$1=" /etc/signlang.env | cut -d= -f2-
}

echo "=== 1. Waiting for the server's first start to finish ==="
cloud-init status --wait > /dev/null || true

# upload.bat sends the web address (for example mysignlang.duckdns.org). Save it, so it wins over the stack's setting.
if [ -n "$1" ]; then
  sudo sed -i "s/^DOMAIN=.*/DOMAIN=$1/" /etc/signlang.env
fi

echo "=== 2. Installing Python, the libraries OpenCV needs, and Caddy (the https:// and login part) ==="
# Graphics libraries a desktop has but a bare server does not:
# libgl1 and libglib2.0-0 for OpenCV, and libegl1 and libgles2 for MediaPipe's hand finder.
sudo apt-get update
sudo apt-get install -y python3-venv libgl1 libglib2.0-0 libegl1 libgles2
if ! command -v caddy > /dev/null; then
  sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gpg
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | sudo gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt | sudo tee /etc/apt/sources.list.d/caddy-stable.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y caddy
fi

echo "=== 3. Installing the Python libraries (same versions as the laptop) ==="
cd "$APP_FOLDER"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip
# The CPU-only PyTorch is much smaller; this server has no graphics card.
.venv/bin/pip install -r deploy/requirements-server.txt --extra-index-url https://download.pytorch.org/whl/cpu

echo "=== 4. Downloading the AI model once (about 372 MB) ==="
.venv/bin/python -c "import backend.signs"

echo "=== 5. Finding the S3 bucket for the photos ==="
# Ask the server's own information page for the AWS account number and region.
TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
IDENTITY=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/dynamic/instance-identity/document)
ACCOUNT=$(echo "$IDENTITY" | python3 -c "import json, sys; print(json.load(sys.stdin)['accountId'])")
REGION=$(echo "$IDENTITY" | python3 -c "import json, sys; print(json.load(sys.stdin)['region'])")
# The bucket name is the same one CloudFormation made: signlang-captures-<account number>.
printf "CAPTURES_BUCKET=signlang-captures-%s\nAWS_DEFAULT_REGION=%s\n" "$ACCOUNT" "$REGION" | sudo tee /etc/signlang-s3.env > /dev/null
echo "Photos will go to the bucket signlang-captures-$ACCOUNT"

echo "=== 6. Making the app start by itself whenever the server starts ==="
sudo cp deploy/signlang.service /etc/systemd/system/signlang.service
sudo systemctl daemon-reload
sudo systemctl enable signlang
sudo systemctl restart signlang

echo "=== 7. Setting up https:// and the login ==="
DOMAIN=$(setting DOMAIN)
LOGIN_USER=$(setting LOGIN_USER)
PASSWORD_HASH=$(caddy hash-password --plaintext "$(setting LOGIN_PASSWORD)")
sudo tee /etc/caddy/Caddyfile > /dev/null <<END
# Made by deploy/setup.sh. Gives the app a secure https:// address and asks for the login.
$DOMAIN {
	basic_auth {
		$LOGIN_USER $PASSWORD_HASH
	}
	reverse_proxy localhost:8000
}
END
sudo systemctl restart caddy

echo
echo "=== Done. Open https://$DOMAIN on the tablet. ==="
echo "The first time, the https:// certificate can take a minute to arrive."

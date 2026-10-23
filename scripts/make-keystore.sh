#!/usr/bin/env bash
# Creates YOUR upload keystore and prints the values to store as GitHub secrets.
# Needs a JDK (keytool). Keep upload.jks backed up and NEVER commit it.
set -euo pipefail
ALIAS="${1:-upload}"
keytool -genkeypair -v -storetype PKCS12 -keystore upload.jks -alias "$ALIAS" \
  -keyalg RSA -keysize 2048 -validity 10000
echo; echo "Add these repository secrets (Settings > Secrets and variables > Actions):"
echo "  ANDROID_KEYSTORE_BASE64   = $(base64 < upload.jks | tr -d '\n' | cut -c1-24)...  (run: base64 -w0 upload.jks   | macOS: base64 -i upload.jks)"
echo "  ANDROID_KEYSTORE_PASSWORD = the store password you just chose"
echo "  ANDROID_KEY_ALIAS         = $ALIAS"
echo "  ANDROID_KEY_PASSWORD      = the key password you just chose"

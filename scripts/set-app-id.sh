#!/usr/bin/env bash
# Usage: scripts/set-app-id.sh com.yourname.calculator
# Run this BEFORE you create the app in Play Console — the package name can never be changed afterwards.
set -euo pipefail
NEW="${1:?usage: $0 <new.package.name>}"
[[ "$NEW" =~ ^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$ ]] || { echo "Invalid package name: $NEW"; exit 1; }
OLD=$(node -p "require('./capacitor.config.json').appId")
sed -i.bak "s/\"appId\": \"$OLD\"/\"appId\": \"$NEW\"/" capacitor.config.json
sed -i.bak "s/applicationId \"$OLD\"/applicationId \"$NEW\"/" android/app/build.gradle
sed -i.bak "s/>$OLD</>$NEW</g" android/app/src/main/res/values/strings.xml
find . -name '*.bak' -not -path './node_modules/*' -delete
sed -i.bak "s/namespace = \"$OLD\"/namespace = \"$NEW\"/" android/app/build.gradle
sed -i.bak "s/^package $OLD;/package $NEW;/" "android/app/src/main/java/${OLD//.//}/MainActivity.java"
mkdir -p "android/app/src/main/java/${NEW//.//}"
mv "android/app/src/main/java/${OLD//.//}/MainActivity.java" "android/app/src/main/java/${NEW//.//}/"
find android/app/src/main/java -type d -empty -delete
find . -name '*.bak' -not -path './node_modules/*' -delete
echo "applicationId + namespace changed: $OLD -> $NEW"

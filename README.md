# Calculator (Android)

Brand-styled calculator (Light + Dark, from the Figma file) packaged for Android with Capacitor 8.
Targets **Android 16 / API 36** (Google Play's current requirement for new apps), min Android 7.0 (API 24). No ads, no analytics, no permissions beyond the Capacitor default `INTERNET`.

```
www/            the app (index.html, style.css, calc.js engine, app.js UI, bundled Inter font)
android/        native Android project (Gradle)
tests/          engine unit tests + headless-browser UI tests
store/          Play Store assets: icon, feature graphic, screenshots, listing copy
scripts/        set-app-id.sh · make-keystore.sh · make_icons.py · feature_graphic.py
.github/workflows/android.yml   cloud build → APK + signed AAB (+ optional Play upload)
```

> **Status:** engine (18 tests) and UI (12 checks, real Chromium) are tested. The Android build itself could not be run in the authoring sandbox (no Android SDK / Google servers), so **your first GitHub Actions run is the first full build**. If it fails, send me the log and I'll fix it.

## 1. Get an APK (about 5 minutes, free)

1. Create a GitHub repo and push this folder:
   `git init && git add . && git commit -m "Calculator" && git branch -M main && git remote add origin <your-repo-url> && git push -u origin main`
2. Open the repo → **Actions → Android build** → open the latest run → download the **calculator-debug-apk** artifact.
3. Unzip, copy `app-debug.apk` to your phone, open it (allow "install unknown apps" when asked).

The debug APK is fully working but debug-signed — fine for testing and sharing, **not** for the Play Store.

## 2. Ship to Google Play

**Before anything:** pick your permanent package name and run
`scripts/set-app-id.sh com.yourname.calculator` (default is `com.broncept.calculator`). It can never be changed after you create the app in Play Console.

1. **Developer account** — [play.google.com/console](https://play.google.com/console), one-time US$25, identity verification. *Personal accounts created after 13 Nov 2023 must run a closed test with ≥12 testers opted in for 14 continuous days before applying for production access; organization accounts are exempt.* Plan ~3 weeks for a first launch.
2. **Upload key** — run `scripts/make-keystore.sh` (needs a JDK). Back up `upload.jks` and its passwords somewhere safe; never commit them. Play App Signing keeps the real signing key; if you lose the upload key you can request a reset.
3. **GitHub secrets** (Settings → Secrets and variables → Actions): `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.
4. Push again (or re-run the workflow) → download **calculator-release** → `app-release.aab` is your Play bundle (and a signed `app-release.apk`).
5. **Play Console → Create app**, then follow `store/PLAY_STORE.md` (listing text, graphics, Data safety answers, content rating). Upload the `.aab` to **Testing → Closed testing** for the first release.
6. After the first manual upload, optional automation: create a Play API service account, add its JSON as the secret `PLAY_SERVICE_ACCOUNT_JSON`, then run the workflow manually with **publish_to_play** ticked (uploads to the internal track).

Each CI run uses `github.run_number` as `versionCode`, so every upload is automatically newer. Tag `v1.2.0` to set the visible version name.

## Accessibility

Target: WCAG 2.2 AA. 58 automated checks run in CI (`npm run test:a11y`): contrast of every key/state and key outline in both
themes, focus visibility, voice-control names, keyboard operation, screen-reader announcements, touch-target
size, reduced motion, portrait/landscape layout. See `store/ACCESSIBILITY.md` for the public statement and the
manual device-testing checklist in `store/PLAY_STORE.md` (TalkBack, Voice Access, Switch Access, largest font).
Automated tests cannot prove full conformance — do the manual pass on a real phone before each release.

## Local development

```bash
npm ci
npm test                      # engine tests
npx cap sync android          # copy www/ into the Android project
cd android && ./gradlew assembleDebug     # needs Android SDK + JDK 21 (or open android/ in Android Studio)
```
Preview in a browser: `cd www && python3 -m http.server 8000`.

## Design tokens

CSS variables in `www/style.css` mirror the Figma collection **Calculator Colors** (Light/Dark). Palette: EBEBEB D7D7D7 C7C7C7 888888 555555 3D3D3D 2D2D2D 1D1D1D · negative DF0000 · warning FF9900 · positive 00E576 · primary/buttons 006AEB. Figma file `Calculator – Wireframe, Design & Prototype` is in sync with these tokens (variable `key/outline` added; states Pending operator, Error and Focus drawn on the Design page). Derived (not in the original palette): `#0055BF` (operator pressed) `#777777` (dark-mode function-key pressed, so the label keeps 3:1) and the key outline `--edge` (`#767676` light / `#8A8A8A` dark, so key shapes keep 3:1 against the page).

# Play Console checklist

## Store listing (copy/paste)
**Developer name (Play Console account):** Broncept
**App name (≤30):** Broncept Calculator
**Short description (≤80):** A clean, fast calculator with light & dark themes. No ads. No tracking.
**Full description:**
A calculator that does one job well.

• Big, readable display with the running expression above the result
• Light and dark themes that follow your phone's setting
• Chained calculations, repeat-equals (2 + 3 = = = → 11), ±, % and decimals
• Handles long numbers: thousands separators, automatic font sizing, clear "can't divide by 0" message
• Built for accessibility: TalkBack and Voice Access support, high-contrast text, follows your system font size, large touch targets, works with Switch Access and keyboards
• No ads. No account. No tracking. Works fully offline.

**Category:** Tools   **Tags:** Calculator, Utility   **Contact email:** <your Broncept support email>   **Privacy policy URL:** host `PRIVACY_POLICY.md` (GitHub Pages, a public gist, or your website)

## Graphics (in this folder)
- App icon 512×512 → `play-icon-512.png`
- Feature graphic 1024×500 → `play-feature-graphic-1024x500.png`
- Phone screenshots (1080×2400, min 2 required) → `screenshots/01…04`
Take extra screenshots on a real device if you want status bars in them.

## Forms
- **App access:** all functionality available without special access
- **Ads:** No ads
- **Content rating (IARC):** answer "No" to everything → Everyone
- **Target audience:** 18+ is simplest (avoids the Families policy requirements)
- **Data safety:** *Does your app collect or share any required user data types?* → **No**. (Calculator has no network features, analytics, accounts or ads.) Data encrypted in transit / deletion request: not applicable.
- **Government / financial / health / news app:** none apply
- **Target API level:** 36 ✔ (already set)

## Release flow
1. Closed testing → create release → upload `app-release.aab` → add ≥12 tester Google accounts (personal accounts) → keep them opted in 14 days
2. Apply for production access → Production → create release → upload the same or a newer bundle → send for review (typically up to a few days)

## Accessibility (do before every release)
1. Host `ACCESSIBILITY.md` on your website and link it from the Play listing / website field.
2. Install **Accessibility Scanner** (Google) on a real phone and scan every state (empty, result, error, light, dark).
3. Manual pass with **TalkBack** (swipe through all keys, do 12 × 3 =), **Voice Access** ("tap 7", "tap plus"),
   **Switch Access**, **Font size = largest** + **Display size = largest**, and landscape. Fix anything odd.
4. Play Console → **Release → Testing → Pre-launch report → Accessibility** tab — resolve every flagged item.
5. Keep the CI result of `tests/a11y.py` (green) with the release — it's your documented, repeatable evidence.

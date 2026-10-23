package com.broncept.calculator;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        applySystemFontScale();
    }

    /**
     * Make the WebView honour the user's system font size (Settings > Display > Font size) so low-vision
     * users get larger text. Capped at 150% so the keypad labels stay inside their keys.
     * The activity is recreated when the font scale changes, so onCreate re-applies this automatically.
     */
    private void applySystemFontScale() {
        if (getBridge() == null || getBridge().getWebView() == null) return;
        int percent = Math.round(getResources().getConfiguration().fontScale * 100f);
        getBridge().getWebView().getSettings().setTextZoom(Math.max(100, Math.min(percent, 150)));
    }
}

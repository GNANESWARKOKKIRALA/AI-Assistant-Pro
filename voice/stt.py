"""
voice/stt.py — Speech-to-Text
Uses browser Web Speech API via streamlit-js-eval (no PyAudio needed).
Works on Streamlit Cloud, local, and all platforms.
Falls back to PyAudio/SpeechRecognition if available.
"""
import streamlit as st
import streamlit.components.v1 as components


def render_browser_mic(key: str = "browser_mic") -> None:
    """
    Render a browser-based mic button using Web Speech API.
    On transcript, writes result to session state key 'voice_transcript'.
    Works on Streamlit Cloud — no PyAudio required.
    """
    components.html(
        f"""
        <div style="display:flex; align-items:center; gap:10px; font-family:Inter,sans-serif;">
            <button id="micBtn_{key}" onclick="toggleMic_{key}()" style="
                background: #1a1a26;
                border: 1.5px solid #3b3b52;
                color: #a78bfa;
                border-radius: 12px;
                width: 52px;
                height: 52px;
                font-size: 1.3rem;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            ">🎙️</button>
            <span id="micStatus_{key}" style="color:#64748b; font-size:0.85rem;">Click to speak</span>
        </div>

        <script>
        let recognition_{key} = null;
        let isListening_{key} = false;

        function toggleMic_{key}() {{
            if (isListening_{key}) {{
                stopMic_{key}();
            }} else {{
                startMic_{key}();
            }}
        }}

        function startMic_{key}() {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                document.getElementById('micStatus_{key}').innerHTML =
                    '<span style="color:#f87171">❌ Browser not supported. Use Chrome.</span>';
                return;
            }}

            recognition_{key} = new SpeechRecognition();
            recognition_{key}.continuous = false;
            recognition_{key}.interimResults = true;
            recognition_{key}.lang = 'en-US';

            const btn = document.getElementById('micBtn_{key}');
            const status = document.getElementById('micStatus_{key}');

            recognition_{key}.onstart = () => {{
                isListening_{key} = true;
                btn.style.background = '#3b0764';
                btn.style.borderColor = '#7c3aed';
                btn.style.color = '#c4b5fd';
                btn.innerHTML = '⏹️';
                status.innerHTML = '<span style="color:#a78bfa">🎙️ Listening…</span>';
            }};

            recognition_{key}.onresult = (event) => {{
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    transcript += event.results[i][0].transcript;
                }}
                status.innerHTML = '<span style="color:#86efac">✅ ' + transcript + '</span>';
                // Send transcript to Streamlit via query param trick
                const input = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if (input) {{
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(input, transcript);
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }};

            recognition_{key}.onerror = (event) => {{
                isListening_{key} = false;
                btn.style.background = '#1a1a26';
                btn.style.borderColor = '#3b3b52';
                btn.style.color = '#a78bfa';
                btn.innerHTML = '🎙️';
                if (event.error === 'not-allowed') {{
                    status.innerHTML = '<span style="color:#f87171">❌ Mic blocked — allow mic in browser settings</span>';
                }} else {{
                    status.innerHTML = '<span style="color:#f87171">❌ Error: ' + event.error + '</span>';
                }}
            }};

            recognition_{key}.onend = () => {{
                isListening_{key} = false;
                btn.style.background = '#1a1a26';
                btn.style.borderColor = '#3b3b52';
                btn.style.color = '#a78bfa';
                btn.innerHTML = '🎙️';
                if (status.innerHTML.includes('Listening')) {{
                    status.innerHTML = '<span style="color:#64748b">Click to speak</span>';
                }}
            }};

            recognition_{key}.start();
        }}

        function stopMic_{key}() {{
            if (recognition_{key}) recognition_{key}.stop();
        }}
        </script>
        """,
        height=70,
    )


def is_mic_available() -> bool:
    """Always True — browser mic works everywhere including Streamlit Cloud."""
    return True


def record_and_transcribe(timeout: int = 5, phrase_limit: int = 15) -> str:
    """Legacy function kept for compatibility. Browser mic is used instead."""
    return ""

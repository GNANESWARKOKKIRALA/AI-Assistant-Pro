"""
voice/stt.py — Browser-based Speech-to-Text via Web Speech API
Injects a mic button that captures voice and fills the chat input.
"""
import streamlit as st
import streamlit.components.v1 as components


def render_browser_mic(key: str = "mic") -> None:
    """
    Render a microphone button using the browser's Web Speech API.
    Captured transcript is injected into the Streamlit chat input via JS.
    """
    mic_html = """
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <button id="micBtn" onclick="toggleMic()" style="
            background: #f0f0f0;
            border: 1.5px solid #d0d0d0;
            border-radius: 50%;
            width: 38px; height: 38px;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: all 0.2s ease;
        " title="Click to speak">🎙️</button>
        <span id="micStatus" style="font-size:0.78rem; color:#888;">Click mic to speak</span>
    </div>

    <script>
    let recognition = null;
    let isListening = false;

    function toggleMic() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('micStatus').innerText = '❌ Browser does not support voice input';
            return;
        }

        if (isListening) {
            recognition.stop();
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        const btn = document.getElementById('micBtn');
        const status = document.getElementById('micStatus');

        recognition.onstart = () => {
            isListening = true;
            btn.style.background = '#fee2e2';
            btn.style.borderColor = '#ef4444';
            btn.innerText = '⏹️';
            status.innerText = '🔴 Listening…';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            status.innerText = '✅ ' + transcript;

            // Inject into Streamlit chat input textarea
            const textareas = window.parent.document.querySelectorAll('textarea');
            textareas.forEach(ta => {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value').set;
                nativeInputValueSetter.call(ta, transcript);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
            });
        };

        recognition.onerror = (event) => {
            status.innerText = '❌ Error: ' + event.error;
            resetBtn();
        };

        recognition.onend = () => {
            isListening = false;
            resetBtn();
        };

        recognition.start();

        function resetBtn() {
            btn.style.background = '#f0f0f0';
            btn.style.borderColor = '#d0d0d0';
            btn.innerText = '🎙️';
        }
    }
    </script>
    """
    components.html(mic_html, height=60)
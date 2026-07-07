# Voice Input for Claude Terminal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A global background script that records mic audio on Shift+Enter toggle, transcribes via ElevenLabs Scribe, and pastes the transcript into the focused window — auto-starting at Windows login.

**Architecture:** A single Python script lives at `~/.claude/tools/voice_input.py` and runs persistently at Windows login via a Startup folder `.bat` launcher. It registers a suppressed global hotkey (Shift+Enter) using the `keyboard` library, records audio via `sounddevice` into a numpy buffer, writes a temp WAV, calls ElevenLabs Scribe, then pastes the result via clipboard + Ctrl+V simulation.

**Tech Stack:** Python 3.x, `keyboard`, `sounddevice`, `scipy`, `numpy`, `pyperclip`, `requests`, `python-dotenv`

---

## File Layout

| Path | Role |
|------|------|
| `<USER_HOME>\.claude\tools\voice_input.py` | Main script — hotkey listener, recorder, transcriber, paster |
| `<USER_HOME>\.claude\tools\start_voice.bat` | Silent launcher (`pythonw`) for Windows Startup |
| `<USER_HOME>\.claude\tools\.env` | `ELEVENLABS_API_KEY=…` — user-managed, never committed |
| `<USER_HOME>\.claude\tools\tests\test_voice_input.py` | Unit tests for transcribe() and on_hotkey() state logic |

---

## Task 1: Install dependencies

**Files:** none created

- [ ] **Step 1: Install Python packages**

```powershell
pip install keyboard sounddevice scipy numpy pyperclip requests python-dotenv
```

Expected output ends with: `Successfully installed ...`

- [ ] **Step 2: Verify keyboard library works**

```powershell
python -c "import keyboard; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Verify sounddevice can see mic**

```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Expected: list of audio devices including at least one input device. If this errors, check that a microphone is connected and enabled in Windows Sound settings.

---

## Task 2: Create tools directory structure

**Files:**
- Create: `<USER_HOME>\.claude\tools\tests\__init__.py`
- Create: `<USER_HOME>\.claude\tools\.env`

- [ ] **Step 1: Create tools and tests directories**

```powershell
New-Item -ItemType Directory -Force "<USER_HOME>\.claude\tools\tests"
```

- [ ] **Step 2: Create empty tests package**

```powershell
New-Item -ItemType File -Force "<USER_HOME>\.claude\tools\tests\__init__.py"
```

- [ ] **Step 3: Create .env with placeholder**

```powershell
Set-Content -Path "<USER_HOME>\.claude\tools\.env" -Value "ELEVENLABS_API_KEY=" -Encoding utf8
```

- [ ] **Step 4: Open .env so user can paste their API key**

Open `<USER_HOME>\.claude\tools\.env` in the IDE/editor. User pastes their ElevenLabs API key after `ELEVENLABS_API_KEY=` and saves.

---

## Task 3: Write `transcribe()` with tests

**Files:**
- Create: `<USER_HOME>\.claude\tools\tests\test_voice_input.py` (stub)
- Create: `<USER_HOME>\.claude\tools\voice_input.py` (stub with `transcribe()` only)

- [ ] **Step 1: Write the failing test**

Create `<USER_HOME>\.claude\tools\tests\test_voice_input.py`:

```python
import os
import sys
from unittest.mock import patch, MagicMock

# Stub heavy deps before importing voice_input
for mod in ('keyboard', 'sounddevice', 'pyperclip'):
    sys.modules.setdefault(mod, MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import voice_input


def test_transcribe_returns_text(tmp_path):
    wav = tmp_path / 'audio.wav'
    wav.write_bytes(b'RIFF' + b'\x00' * 36)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'text': 'hello world'}

    with patch('voice_input.requests.post', return_value=mock_resp):
        result = voice_input.transcribe(str(wav))

    assert result == 'hello world'


def test_transcribe_returns_none_on_api_error(tmp_path):
    wav = tmp_path / 'audio.wav'
    wav.write_bytes(b'RIFF' + b'\x00' * 36)

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = 'Unauthorized'

    with patch('voice_input.requests.post', return_value=mock_resp):
        result = voice_input.transcribe(str(wav))

    assert result is None


def test_transcribe_returns_none_on_blank_text(tmp_path):
    wav = tmp_path / 'audio.wav'
    wav.write_bytes(b'RIFF' + b'\x00' * 36)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'text': '   '}

    with patch('voice_input.requests.post', return_value=mock_resp):
        result = voice_input.transcribe(str(wav))

    assert result is None
```

- [ ] **Step 2: Run tests — expect ImportError (voice_input doesn't exist yet)**

```powershell
cd "<USER_HOME>\.claude\tools"
python -m pytest tests/test_voice_input.py -v 2>&1 | Select-Object -First 20
```

Expected: `ModuleNotFoundError: No module named 'voice_input'`

- [ ] **Step 3: Create voice_input.py with transcribe() only**

Create `<USER_HOME>\.claude\tools\voice_input.py`:

```python
import os
import sys
import time
import tempfile
import threading
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
import pyperclip
import keyboard
import requests
from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(_ENV_PATH)
API_KEY = os.getenv('ELEVENLABS_API_KEY')

SAMPLE_RATE = 16000

_state_lock = threading.Lock()
_recording = False
_audio_chunks: list = []
_stream = None


def transcribe(wav_path: str):
    with open(wav_path, 'rb') as f:
        resp = requests.post(
            'https://api.elevenlabs.io/v1/speech-to-text',
            headers={'xi-api-key': API_KEY},
            files={'file': ('audio.wav', f, 'audio/wav')},
            data={'model_id': 'scribe_v1'},
            timeout=30,
        )
    if resp.status_code != 200:
        print(f'[error] API {resp.status_code}: {resp.text[:120]}', flush=True)
        return None
    return resp.json().get('text', '').strip() or None
```

- [ ] **Step 4: Run tests — expect PASS**

```powershell
python -m pytest tests/test_voice_input.py -v
```

Expected:
```
test_voice_input.py::test_transcribe_returns_text PASSED
test_voice_input.py::test_transcribe_returns_none_on_api_error PASSED
test_voice_input.py::test_transcribe_returns_none_on_blank_text PASSED
3 passed
```

- [ ] **Step 5: Commit**

```powershell
cd "<USER_HOME>\.claude\tools"
git init  # only if not already a git repo
git add voice_input.py tests/
git commit -m "feat: add voice_input transcribe() with tests"
```

---

## Task 4: Add audio recorder

**Files:**
- Modify: `<USER_HOME>\.claude\tools\voice_input.py` — add `_audio_callback`, `_start_recording`, `_stop_and_transcribe`
- Modify: `<USER_HOME>\.claude\tools\tests\test_voice_input.py` — add recorder tests

- [ ] **Step 1: Write failing tests for recorder flow**

Append to `tests/test_voice_input.py`:

```python
def test_stop_and_transcribe_pastes_text(tmp_path):
    import numpy as np

    chunk = np.zeros((1600, 1), dtype='int16')
    voice_input._audio_chunks = [chunk]
    voice_input._recording = True

    mock_stream = MagicMock()
    voice_input._stream = mock_stream

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {'text': 'test paste'}

    with patch('voice_input.requests.post', return_value=mock_resp), \
         patch('voice_input.pyperclip.copy') as mock_copy, \
         patch('voice_input.keyboard.send') as mock_send, \
         patch('voice_input.time.sleep'):
        voice_input._stop_and_transcribe()

    mock_copy.assert_called_once_with('test paste')
    mock_send.assert_called_once_with('ctrl+v')


def test_stop_and_transcribe_handles_empty_buffer():
    voice_input._audio_chunks = []
    voice_input._recording = True

    mock_stream = MagicMock()
    voice_input._stream = mock_stream

    with patch('voice_input.pyperclip.copy') as mock_copy:
        voice_input._stop_and_transcribe()

    mock_copy.assert_not_called()
```

- [ ] **Step 2: Run tests — expect FAIL**

```powershell
python -m pytest tests/test_voice_input.py::test_stop_and_transcribe_pastes_text tests/test_voice_input.py::test_stop_and_transcribe_handles_empty_buffer -v
```

Expected: `AttributeError: module 'voice_input' has no attribute '_stop_and_transcribe'`

- [ ] **Step 3: Add recorder functions to voice_input.py**

Append to `voice_input.py` after the `transcribe()` function:

```python
def _audio_callback(indata, frames, time_info, status):
    _audio_chunks.append(indata.copy())


def _start_recording():
    global _recording, _audio_chunks, _stream
    _audio_chunks = []
    _stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        callback=_audio_callback,
    )
    _stream.start()
    _recording = True
    print('[REC] recording... press Shift+Enter to stop', flush=True)


def _stop_and_transcribe():
    global _recording, _stream
    _recording = False
    _stream.stop()
    _stream.close()
    _stream = None

    if not _audio_chunks:
        print('[error] no audio captured', flush=True)
        return

    print('[transcribing...]', flush=True)
    audio = np.concatenate(_audio_chunks, axis=0)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp = f.name
    try:
        wavfile.write(tmp, SAMPLE_RATE, audio)
        text = transcribe(tmp)
    finally:
        os.unlink(tmp)

    if not text:
        print('[error] empty transcript', flush=True)
        return

    pyperclip.copy(text)
    time.sleep(0.15)
    keyboard.send('ctrl+v')
    print(f'[done] "{text[:60]}"', flush=True)
```

- [ ] **Step 4: Run all tests — expect PASS**

```powershell
python -m pytest tests/test_voice_input.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```powershell
git add voice_input.py tests/test_voice_input.py
git commit -m "feat: add audio recorder and stop/transcribe/paste flow"
```

---

## Task 5: Add hotkey handler and main()

**Files:**
- Modify: `<USER_HOME>\.claude\tools\voice_input.py` — add `on_hotkey()` and `main()`
- Modify: `<USER_HOME>\.claude\tools\tests\test_voice_input.py` — add toggle tests

- [ ] **Step 1: Write failing tests for on_hotkey toggle**

Append to `tests/test_voice_input.py`:

```python
def test_on_hotkey_starts_recording_when_idle():
    voice_input._recording = False

    with patch.object(voice_input, '_start_recording') as mock_start:
        voice_input.on_hotkey()

    mock_start.assert_called_once()


def test_on_hotkey_stops_when_recording():
    voice_input._recording = True

    with patch('threading.Thread') as mock_thread:
        mock_thread.return_value.start = MagicMock()
        voice_input.on_hotkey()

    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()
```

- [ ] **Step 2: Run tests — expect FAIL**

```powershell
python -m pytest tests/test_voice_input.py::test_on_hotkey_starts_recording_when_idle tests/test_voice_input.py::test_on_hotkey_stops_when_recording -v
```

Expected: `AttributeError: module 'voice_input' has no attribute 'on_hotkey'`

- [ ] **Step 3: Add on_hotkey() and main() to voice_input.py**

Append to `voice_input.py`:

```python
def on_hotkey():
    with _state_lock:
        if not _recording:
            _start_recording()
        else:
            threading.Thread(target=_stop_and_transcribe, daemon=True).start()


def main():
    if not API_KEY:
        print('[error] ELEVENLABS_API_KEY not set. Edit:', flush=True)
        print(f'  {_ENV_PATH}', flush=True)
        sys.exit(1)

    print('Voice input ready. Shift+Enter = start / stop.', flush=True)
    keyboard.add_hotkey('shift+enter', on_hotkey, suppress=True)
    keyboard.wait()


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Run all tests — expect PASS**

```powershell
python -m pytest tests/test_voice_input.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```powershell
git add voice_input.py tests/test_voice_input.py
git commit -m "feat: add hotkey handler and main entrypoint"
```

---

## Task 6: Create launcher and add to Windows Startup

**Files:**
- Create: `<USER_HOME>\.claude\tools\start_voice.bat`

- [ ] **Step 1: Create the silent launcher**

Create `<USER_HOME>\.claude\tools\start_voice.bat`:

```bat
@echo off
start /B pythonw "<USER_HOME>\.claude\tools\voice_input.py"
```

`pythonw` runs Python with no console window.

- [ ] **Step 2: Test the launcher manually**

```powershell
& "<USER_HOME>\.claude\tools\start_voice.bat"
```

Expected: no window appears. Check Task Manager → Details for a `pythonw.exe` process. Press Shift+Enter somewhere — you should hear nothing yet (no mic feedback) but the process is running.

Kill it:
```powershell
Stop-Process -Name "pythonw" -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 3: Add bat file to Windows Startup folder**

```powershell
$startup = [System.Environment]::GetFolderPath('Startup')
Copy-Item "<USER_HOME>\.claude\tools\start_voice.bat" "$startup\voice_input.bat" -Force
Write-Host "Added to: $startup\voice_input.bat"
```

Expected: prints the path — something like `<USER_HOME>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\voice_input.bat`

- [ ] **Step 4: Verify startup entry exists**

```powershell
$startup = [System.Environment]::GetFolderPath('Startup')
Test-Path "$startup\voice_input.bat"
```

Expected: `True`

- [ ] **Step 5: Commit**

```powershell
git add start_voice.bat
git commit -m "feat: add Windows startup launcher"
```

---

## Task 7: End-to-end smoke test

- [ ] **Step 1: Start the script in a visible terminal (for feedback)**

```powershell
python "<USER_HOME>\.claude\tools\voice_input.py"
```

Expected: `Voice input ready. Shift+Enter = start / stop.`

- [ ] **Step 2: Focus Claude Code terminal, press Shift+Enter**

Expected: background terminal prints `[REC] recording... press Shift+Enter to stop`

- [ ] **Step 3: Speak a short phrase (e.g. "hello this is a test"), press Shift+Enter**

Expected: background terminal prints `[transcribing...]` then `[done] "hello this is a test"`
And the transcript appears pasted in the Claude Code input box.

- [ ] **Step 4: If paste doesn't land in Claude Code**

Some terminals use bracketed paste mode. Try: after `[done]` prints, manually Ctrl+V in the Claude Code terminal — the transcript should be in the clipboard.

- [ ] **Step 5: Stop the script (Ctrl+C in its terminal)**

- [ ] **Step 6: Open .env to confirm API key is set**

Open `<USER_HOME>\.claude\tools\.env`. Confirm it reads:
```
ELEVENLABS_API_KEY=<your_key_here>
```

If blank, paste the key and save before running again.

---

## Known Limitations

- **Newline side effect:** If `suppress=True` doesn't work as expected on some Windows Terminal versions, Shift+Enter may also insert a newline into the focused app. Delete it before submitting if it appears.
- **Single instance:** Running two copies of the script will conflict on the hotkey. If the script seems unresponsive, check Task Manager for stale `pythonw.exe` processes and kill them.
- **Clipboard clobber:** The paste step replaces clipboard contents. If you had something important in the clipboard, it will be gone after transcription.

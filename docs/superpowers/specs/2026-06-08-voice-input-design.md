# Voice Input for Claude Terminal — Design Spec
**Date:** 2026-06-08

## Overview

A global, always-on speech-to-text tool that lets the user dictate messages into the Claude Code terminal (or any focused window) using Shift+Enter as a toggle.

## Goals

- Works globally across all projects — not tied to any single repo
- Auto-starts at Windows login, no manual launch needed
- Shift+Enter toggles recording on/off; transcript is pasted at cursor on stop
- Uses ElevenLabs Scribe for transcription (same engine as video workflow)

## File Layout

```
<USER_HOME>\.claude\tools\
  voice_input.py       ← main script (listener + recorder + transcriber)
  start_voice.bat      ← silent launcher (used by Windows Startup entry)
  .env                 ← ELEVENLABS_API_KEY (user-managed, never committed)
```

## Architecture

### Hotkey Listener
- `pynput.keyboard.GlobalHotKeys` listens for `<shift>+<return>` system-wide
- The key event is **suppressed** so it never reaches the focused app
- On first press: start recording; on second press: stop and transcribe

### Audio Recording
- `sounddevice.InputStream` captures mic audio into a `numpy` array buffer
- Sample rate: 16 kHz mono (optimal for speech, small file size)
- Buffer accumulates while recording; written to a temp WAV via `scipy.io.wavfile`

### Transcription
- POSTs the WAV to ElevenLabs Scribe (`/v1/speech-to-text`)
- API key loaded from `~/.claude/tools/.env` via `python-dotenv`
- Returns plain text transcript

### Paste to Focused Window
- Transcript is written to clipboard via `pyperclip`
- `pynput.keyboard.Controller` simulates Ctrl+V to paste into the active window
- Works in Claude Code terminal, VS Code, Notepad, browser — any focused text input

### Visual Feedback
- Prints status lines to the background terminal:
  - `[REC]` — recording started
  - `[transcribing...]` — API call in progress
  - `[done] "<first 60 chars of transcript>"` — pasted successfully
  - `[error] <message>` — if API call fails

## Windows Auto-Start

`start_voice.bat` contains:
```bat
@echo off
start /B pythonw "<USER_HOME>\.claude\tools\voice_input.py"
```

This `.bat` file is placed (or symlinked) in:
`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

The script then runs silently at every login.

## Dependencies

All installable via pip:
```
sounddevice
scipy
pyperclip
pynput
python-dotenv
requests
```

## Error Handling

- If mic is not available: prints `[error] no input device found` and exits cleanly
- If API key is missing: prints `[error] ELEVENLABS_API_KEY not set in ~/.claude/tools/.env`
- If transcription fails: prints `[error] <HTTP status>` and clears recording state (ready for next attempt)
- If clipboard/paste fails: falls back to printing the transcript to the terminal so the user can copy manually

## Out of Scope

- Wake word / always-listening mode
- Per-project config overrides
- Audio playback / confirmation tone



# Speech-to-Speech Recognition System

## Overview
This project enables transforming audio from video files into transcribed text, translating that text into a target language, and generating speech in the target language. It merges the translated speech with the original video, producing a multilingual video output.

### Key Features
- Process videos from a URL or uploaded files.
- Extract audio and transcribe it to text.
- Translate transcriptions into the chosen target language.
- Generate speech from the translated text.
- Merge the generated speech back into the original video.

---

## Project Structure

### Backend
The backend is built using **Flask** and provides RESTful API endpoints to process videos, extract audio, transcribe, translate, generate speech, and merge audio-video.

### Frontend
The frontend is built using **React**, providing a simple and intuitive UI for:
- Uploading or linking videos.
- Selecting a target language.
- Displaying processing steps and final output.

---

## Requirements

### Backend
1. **Python** (3.8 or higher).
2. Python Libraries:
   - Flask
   - Flask-CORS
   - ffmpeg-python
   - yt-dlp
   - openai-whisper
   - googletrans
   - gTTS

3. **FFmpeg** (installed and configured for audio-video processing).

### Frontend
1. **Node.js** (for React development).
2. React Libraries:
   - Axios (for API calls).

---

## Usage

### Backend
- Start the Flask server to handle API requests.

### Frontend
- Start the React app and interact with the UI to:
  - Enter a video URL or upload a local file.
  - Select the target language for translation.
  - Monitor progress and get the final processed video path.

---

## Endpoints
1. **/process-video**: Processes a video from a given URL.
2. **/process-video-file**: Processes an uploaded video file.
3. **/download**: Downloads a video from a URL.
4. **/extract-audio**: Extracts audio from a video.
5. **/transcribe**: Transcribes audio to text.
6. **/translate**: Translates text to the target language.
7. **/text-to-speech**: Converts translated text to speech.
8. **/merge**: Merges the generated speech with the original video.

---

## Technologies Used
- **Backend**:
  - Flask for API development.
  - FFmpeg for media processing.
  - OpenAI Whisper for transcription.
  - gTTS for text-to-speech conversion.
  - Google Translate API for text translation.

- **Frontend**:
  - React for building the user interface.
  - Axios for making API requests to the backend.

---

## How It Works
1. **Input**:
   - Video URL or uploaded local video.
   - Target language selection (e.g., Hindi, Telugu, etc.).

2. **Workflow**:
   - Backend:
     - Downloads/accepts the video.
     - Extracts audio.
     - Transcribes audio to text.
     - Translates transcribed text to the selected language.
     - Converts translated text to speech.
     - Merges new audio with the original video.
   - Frontend:
     - Sends requests to the backend and displays progress and results.

3. **Output**:
   - The final multilingual video file is accessible through the provided path.

---

## Supported Languages
- Hindi (hi)
- Telugu (te)
- Bengali (bn)
- Marathi (mr)
- Tamil (ta)
- Urdu (ur)
- Gujarati (gu)
- Malayalam (ml)
- Kannada (kn)
- Odia (or)
- Punjabi (pa)
- Assamese (as)

---

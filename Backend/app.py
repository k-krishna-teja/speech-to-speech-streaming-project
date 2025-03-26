from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import ffmpeg
import whisper
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import subprocess
import json
import yt_dlp

app = Flask(__name__)
CORS(app)

  # Enable CORS for frontend-backend communication

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


@app.before_request
def log_request_info():
    print(f"Headers: {request.headers}")  # Log the request headers
    # Check if multipart form-data is being received
    if request.content_type and "multipart/form-data" in request.content_type:
        print("Multipart form-data received, skipping raw body logging.")
    else:
        # Log the raw request body (if not multipart form-data)
        print(f"Body: {request.get_data(as_text=True)}")  # Decode as text for better readability
# Helper Functions
def download_video(url, output_path):
    try:
        # Set format for low quality video+audio
        ydl_opts = {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',  # Set max resolution to 480p
            'outtmpl': output_path,               # Output file path
            'quiet': False,                       # Enable detailed logs
            'merge_output_format': 'mp4',         # Output format as MP4
            'noplaylist': True,                   # Download a single video, not a playlist
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Video downloaded successfully: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return f"Error downloading video: {e}"
    

def convert_audio_codec(input_video, output_video):
    try:
        ffmpeg.input(input_video).output(output_video, vcodec='copy', acodec='aac').run(overwrite_output=True)
        print(f"Audio codec converted successfully. Output file: {output_video}")
        return True
    except ffmpeg.Error as e:
        print(f"Error converting audio codec: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False

@app.route('/process-video', methods=['POST'])
@app.route('/process-video', methods=['POST'])
def process_video():
    try:
        # Log incoming request data
        print(f"Request received: {request.json}")
        
        # Extract video URL and target language from the request
        input_video = request.json.get('input_video')
        target_language = request.json.get('target_language', 'hi')

        # Step 1: Download video from the provided URL
        print("Downloading video...")
        downloaded_video_path = os.path.join(output_dir, 'downloaded_video.mp4')
        download_result = download_video(input_video, downloaded_video_path)
        if "Error" in download_result:
            print(f"Download error: {download_result}")
            return jsonify({"error": download_result}), 400
        print(f"Video downloaded successfully: {downloaded_video_path}")

        # Step 2: Convert audio codec (to fix Opus issues)
        print("Converting audio codec...")
        converted_video_path = os.path.join(output_dir, 'converted_video.mp4')
        if not convert_audio_codec(downloaded_video_path, converted_video_path):
            return jsonify({"error": "Failed to convert audio codec"}), 400
        print(f"Audio codec converted successfully: {converted_video_path}")

        # Step 3: Extract audio from the video
        print("Extracting audio...")
        audio_file = os.path.join(output_dir, 'extracted_audio.wav')
        extract_result = extract_audio(converted_video_path, audio_file)
        if not extract_result:
            return jsonify({"error": "Audio extraction failed"}), 400
        print(f"Audio extracted: {audio_file}")

        # Step 4: Transcribe audio to text
        print("Transcribing audio...")
        transcribed_text = transcribe_audio(audio_file)
        if not transcribed_text:
            return jsonify({"error": "Transcription failed"}), 400
        print(f"Transcription result: {transcribed_text}")

        # Step 5: Translate text to the target language
        print("Translating text...")
        translated_text = translate_text(transcribed_text, target_language)
        if not translated_text:
            return jsonify({"error": "Translation failed"}), 400
        print(f"Translation result: {translated_text}")

        # Step 6: Convert translated text to speech (TTS)
        print("Converting text to speech...")
        translated_audio_file = os.path.join(output_dir, f'translated_audio_{target_language}.mp3')
        tts_result = text_to_speech(translated_text, translated_audio_file, target_language)
        if not tts_result:
            return jsonify({"error": "Text-to-Speech failed"}), 400
        print(f"Translated audio file created: {translated_audio_file}")

        # Step 7: Merge translated audio with original video
        print("Merging audio with video...")
        final_video_path = os.path.join(output_dir, 'final_video.mp4')
        merge_result = merge_audio_with_video(converted_video_path, translated_audio_file, final_video_path)
        if not merge_result:
            return jsonify({"error": "Merging video and audio failed"}), 400
        print(f"Final video created: {final_video_path}")

        # Return success response
        return jsonify({"message": "Processing completed", "output_video": final_video_path})

    except Exception as e:
        print(f"Error encountered: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/process-video-file', methods=['POST'])
def process_video_file():
    try:
        # Retrieve the uploaded file and target language from the request
        file = request.files['file']
        target_language = request.form.get('target_language', 'hi')

        # Save the uploaded file to the output directory
        input_file_path = os.path.join(output_dir, file.filename)
        file.save(input_file_path)

        # Process the video
        audio_file = os.path.join(output_dir, 'extracted_audio.wav')
        extract_result = extract_audio(input_file_path, audio_file)
        if not extract_result:
            return jsonify({"error": "Audio extraction failed"}), 400

        transcribed_text = transcribe_audio(audio_file)
        if not transcribed_text:
            return jsonify({"error": "Transcription failed"}), 400

        translated_text = translate_text(transcribed_text, target_language)
        if not translated_text:
            return jsonify({"error": "Translation failed"}), 400

        translated_audio_file = os.path.join(output_dir, f'translated_audio_{target_language}.mp3')
        tts_result = text_to_speech(translated_text, translated_audio_file, target_language)
        if not tts_result:
            return jsonify({"error": "Text-to-Speech failed"}), 400

        output_video_file = os.path.join(output_dir, 'final_video.mp4')
        merge_result = merge_audio_with_video(input_file_path, translated_audio_file, output_video_file)
        if not merge_result:
            return jsonify({"error": "Merging video and audio failed"}), 400

        return jsonify({"message": "Processing completed", "output_video": output_video_file})
    except Exception as e:
        print(f"Error processing local video: {e}")
        return jsonify({"error": str(e)}), 500

def fix_audio_codec(input_video, output_video):
    try:
        # Using ffmpeg to copy video stream and re-encode audio stream to AAC
        ffmpeg.input(input_video).output(output_video, vcodec='copy', acodec='aac').run(overwrite_output=True)
        print(f"Audio codec fixed successfully. Output file: {output_video}")
        return True
    except ffmpeg.Error as e:
        print(f"Error fixing audio codec: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False
    
    
def extract_audio(input_video, output_audio):
    try:
        print(f"Extracted audio file:")
        print(f"Extracting audio from {input_video} to {output_audio}")
        ffmpeg.input(input_video).output(output_audio, ac=1, ar='16000').run(quiet=False, overwrite_output=True)
        print(f"Audio extracted successfully: {output_audio}")
        print(f"Extracted audio path:")
        return True
    except ffmpeg.Error as e:
        print(f"Error extracting audio: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False

def transcribe_audio(audio_file):
    try:
        print(f"Transcription result:")
        model = whisper.load_model("base")
        return model.transcribe(audio_file)["text"]
    except Exception as e:
        return f"Error transcribing audio: {e}"

def translate_text(text, target_language):
    try:
        print(f"Translated text: ")
        translator = Translator()
        return translator.translate(text, dest=target_language).text 
    
    except Exception as e:
        return f"Error translating text: {e}"

def text_to_speech(text, output_file, language):
    try:
        tts = gTTS(text, lang=language)
        tts.save(output_file)
        return True
    except Exception as e:
        return f"Error converting text to speech: {e}"

def merge_audio_with_video(original_video, translated_audio, output_video):
    try:
        video_stream = ffmpeg.input(original_video)
        audio_stream = ffmpeg.input(translated_audio)
        ffmpeg.output(
            video_stream['v'],  # Map video stream
            audio_stream['a'],  # Map audio stream
            output_video,
            vcodec='copy',
            acodec='aac',
            strict='experimental'
        ).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        return f"Error merging video and audio: {e.stderr.decode() if e.stderr else 'Unknown error'}"

# Routes
@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        output_path = os.path.join(output_dir, 'downloaded_video.mp4')
        download_result = download_video(url, output_path)
        if 'Error' in download_result:
            return jsonify({"error": download_result}), 400
        return jsonify({"message": "Video downloaded successfully", "path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract-audio', methods=['POST'])
def extract_audio_route():
    try:
        data = request.json
        input_video = data.get('input_video')
        audio_file = os.path.join(output_dir, 'extracted_audio.wav')
        extract_result = extract_audio(input_video, audio_file)
        if extract_result is not True:
            return jsonify({"error": extract_result}), 400
        return jsonify({"message": "Audio extracted successfully", "path": audio_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        audio_file = data.get('audio_file')
        transcribed_text = transcribe_audio(audio_file)
        if 'Error' in transcribed_text:
            return jsonify({"error": transcribed_text}), 400
        return jsonify({"message": "Transcription completed", "transcription": transcribed_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('target_language', 'hi')
        translated_text = translate_text(text, target_language)
        if 'Error' in translated_text:
            return jsonify({"error": translated_text}), 400
        return jsonify({"message": "Translation completed", "translation": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def tts():
    try:
        data = request.json
        text = data.get('text')
        language = data.get('language', 'hi')
        output_file = os.path.join(output_dir, 'translated_audio.mp3')
        tts_result = text_to_speech(text, output_file, language)
        if tts_result is not True:
            return jsonify({"error": tts_result}), 400
        return jsonify({"message": "Text-to-Speech completed", "path": output_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/merge', methods=['POST'])
def merge():
    try:
        data = request.json
        original_video = data.get('original_video')
        translated_audio = data.get('translated_audio')
        output_video = os.path.join(output_dir, 'final_video.mp4')

        merge_result = merge_audio_with_video(original_video, translated_audio, output_video)
        if merge_result is not True:
            return jsonify({"error": merge_result}), 400
        return jsonify({"message": "Merge completed", "output_video": output_video})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main Function
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
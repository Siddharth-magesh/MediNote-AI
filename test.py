from flask import Flask, jsonify, request
import os
import pyaudio
import wave
import uuid
from google.cloud import speech
from pydub import AudioSegment, silence
import threading
import json
from googletrans import Translator 

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"P:/hackathons/hack-verse/serviceacc_key.json"  

stream = None
frames = []
output_filename = None

translator = Translator()

def start_recording_thread(sample_rate=44100, channels=1, chunk_size=1024):
    global stream, frames, output_filename

    unique_id = "PAT" + str(uuid.uuid4().int)[:3]
    
    base_folder = "static/patient_details"
    patient_folder = os.path.join(base_folder, unique_id)
    
    os.makedirs(patient_folder, exist_ok=True)

    output_filename = os.path.join(patient_folder, "recording.wav")

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,  
                    channels=channels,  
                    rate=sample_rate, 
                    input=True, 
                    frames_per_buffer=chunk_size)  

    print("Recording started... Press stop to end.")

    frames = [] 

    while stream.is_active():
        data = stream.read(chunk_size)
        frames.append(data)

def stop_recording(sample_rate=44100, channels=1):
    global stream, frames, output_filename

    if stream is not None:
        stream.stop_stream()
        stream.close()

        p = pyaudio.PyAudio()
        p.terminate()

        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(channels)  
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16)) 
            wf.setframerate(sample_rate)  
            wf.writeframes(b''.join(frames)) 

        print(f"Audio saved as {output_filename}")
        return output_filename 
    else:
        print("Recording was not started.")
        return None

def split_audio_on_silence(file_path, silence_thresh=-40, min_silence_len=500):
    audio = AudioSegment.from_file(file_path)
    segments = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=200,
    )
    return segments

def transcribe_segment(segment, language_code):
    client = speech.SpeechClient()
    segment.export("temp_segment.wav", format="wav")
    with open("temp_segment.wav", "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=segment.frame_rate,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
    return None

def process_audio_with_language(file_path, language_code):
    segments = split_audio_on_silence(file_path)
    transcripts = []
    for segment in segments:
        transcript = transcribe_segment(segment, language_code)
        if transcript:
            if language_code != 'en':
                translated_text = translator.translate(transcript, src=language_code, dest='en').text
                transcripts.append({"language": language_code, "transcript": transcript, "translated": translated_text})
            else:
                transcripts.append({"language": language_code, "transcript": transcript})
    return transcripts

def save_transcripts_to_json(transcripts, folder, file_name="transcript.json"):
    try:
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, file_name)

        with open(file_path, 'w') as json_file:
            json.dump({"transcripts": transcripts}, json_file, indent=4)

        print(f"Transcripts saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error while saving JSON: {e}")
        raise

@app.route('/start-recording', methods=['POST'])
def start_recording():
    thread = threading.Thread(target=start_recording_thread)
    thread.start()
    return jsonify({"message": "Recording started"}), 200

@app.route('/stop-recording', methods=['POST'])
def stop_recording_endpoint():
    file_path = stop_recording()
    language_code = request.form.get("language_select")
    if file_path:
        folder = os.path.dirname(file_path)

        transcripts = process_audio_with_language(file_path,language_code)
        if transcripts:
            save_transcripts_to_json(transcripts, folder)
            return jsonify({"message": "Transcription successful", "transcripts": transcripts}), 200
        else:
            return jsonify({"message": "Failed to transcribe audio"}), 500
    else:
        return jsonify({"message": "Failed to stop recording"}), 500

if __name__ == '__main__':
    app.run(debug=True)

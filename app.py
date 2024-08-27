import streamlit as st
from yt_dlp import YoutubeDL
import whisper
from moviepy.editor import VideoFileClip
import ffmpeg
import os
from deep_translator import GoogleTranslator
import re
import concurrent.futures


def load_css(file_name="static/style.css"):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css()

cookie_file = "cookies.txt"


def download_video(video_url, cookie_file=None, proxy=None):
    ydl_opts = {
        "format": "best",
        "outtmpl": "input_video.%(ext)s",
        "noplaylist": True,
        "nocheckcertificate": True,
    }

    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(result)


def extract_audio(video_file):
    audio_file = "input_audio.mp3"
    video = VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    return audio_file


def generate_subtitles(audio_file, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file)
    return result["segments"]


def save_transcript_to_srt(segments, output_srt="input_srt.srt"):
    with open(output_srt, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"].strip()

            start_timestamp = convert_seconds_to_srt_timestamp(start_time)
            end_timestamp = convert_seconds_to_srt_timestamp(end_time)

            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{start_timestamp} --> {end_timestamp}\n")
            srt_file.write(f"{text}\n\n")


def convert_seconds_to_srt_timestamp(seconds):
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def translate_text(text, dest_language):
    try:
        translated = GoogleTranslator(source="auto", target=dest_language).translate(
            text
        )
        return translated
    except Exception as e:
        st.error(f"Error translating text: {text}\nError: {e}")
        return text


def read_srt_file(srt_file):
    with open(srt_file, "r", encoding="utf-8") as file:
        content = file.read()

    subtitles = re.split(r"\n\n", content)

    parsed_subtitles = []
    for subtitle in subtitles:
        match = re.match(
            r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.+)",
            subtitle,
            re.DOTALL,
        )
        if match:
            index = match.group(1)
            timing = match.group(2)
            text = match.group(3).replace("\n", " ")
            parsed_subtitles.append((index, timing, text))

    return parsed_subtitles


def translate_srt(srt_file, dest_language, output_file="translated_srt.srt"):
    subtitles = read_srt_file(srt_file)

    translated_subtitles = []
    for index, timing, text in subtitles:
        translated_text = translate_text(text, dest_language)
        translated_subtitles.append(f"{index}\n{timing}\n{translated_text}\n")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(translated_subtitles))

def process_subtitles(audio_file, srt_file):
    segments = generate_subtitles(audio_file)
    save_transcript_to_srt(segments, srt_file)
    return srt_file


def translate_subtitles(srt_file, dest_language, translated_srt_file):
    translate_srt(srt_file, dest_language, translated_srt_file)
    return translated_srt_file


def main():
    languages_supported = {"Malayalam": "ml", "Telugu": "te", "Hindi": "hi"}
    st.title("Video CC Translation App for Manappuram Finance Limited")
    st.logo("MFL-logo.png")
    video_url = st.text_input(
        "Enter YouTube Video URL",
        placeholder="Please enter a valid YouTube video URL...",
    )
    st.markdown(
        """
    <style>
    .small-font {
        font-size:12px;
        margin-top:-20px;
        font-style: italic;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="small-font" style="color:black;">**Only English videos supported as input</p>',
        unsafe_allow_html=True,
    )
    selected_language = st.selectbox(
        "Select your target language to transcribe the captions.",
        tuple(languages_supported.keys()),
        placeholder="Choose an option",
    )
    dest_language = languages_supported[selected_language]
    if st.button("Process Video"):
        if video_url and dest_language:
            listed_files = os.listdir(os.getcwd())
            files_to_del = {
                "translated_srt.srt",
                "input_video.mp4",
                "final_video.mp4",
                "input_srt.srt",
                "input_audio.mp3",
            }
            common_elements = set(listed_files).intersection(files_to_del)
            final_files_to_del = list(common_elements)
            for file in final_files_to_del:
                os.remove(os.path.join(os.getcwd(), file))
            with st.spinner("Downloading video..."):
                video_file = download_video(video_url, cookie_file=cookie_file)

            st.success("Video downloaded successfully!")

            with st.spinner("Extracting audio..."):
                audio_file = extract_audio(video_file)

            st.success("Audio extracted successfully!")

            srt_file = "input_srt.srt"
            translated_srt_file = "translated_srt.srt"

            with st.spinner("Processing subtitles..."):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_gen = executor.submit(
                        process_subtitles, audio_file, srt_file
                    )
                    future_trans = executor.submit(
                        translate_subtitles,
                        future_gen.result(),
                        dest_language,
                        translated_srt_file,
                    )

                    # Wait for both tasks to complete
                    future_gen.result()
                    future_trans.result()

            st.success("Subtitles generated and translated successfully!")

            st.video('input_video.mp4', subtitles='translated_srt.srt')
        else:
            st.error("Please provide a valid video URL and destination language.")


if __name__ == "__main__":
    main()

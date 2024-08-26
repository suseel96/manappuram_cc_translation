# import streamlit as st
# from yt_dlp import YoutubeDL
# import whisper
# from moviepy.editor import VideoFileClip
# import ffmpeg
# import os
# from deep_translator import GoogleTranslator
# import re
# import uuid

# def download_video(video_url):
#     ydl_opts = {
#         "format": "best",
#         "outtmpl": f"processed_.%(ext)s",
#     }
#     with YoutubeDL(ydl_opts) as ydl:
#         result = ydl.extract_info(video_url, download=True)
#         return ydl.prepare_filename(result)


# def extract_audio(video_file):
#     audio_file = video_file.rsplit(".", 1)[0] + ".mp3"
#     video = VideoFileClip(video_file)
#     video.audio.write_audiofile(audio_file)
#     return audio_file


# def generate_subtitles(audio_file, model_name="base"):
#     model = whisper.load_model(model_name)
#     result = model.transcribe(audio_file)
#     return result["segments"]


# def save_transcript_to_srt(segments, output_srt):
#     with open(output_srt, "w") as srt_file:
#         for i, segment in enumerate(segments):
#             start_time = segment["start"]
#             end_time = segment["end"]
#             text = segment["text"].strip()

#             start_timestamp = convert_seconds_to_srt_timestamp(start_time)
#             end_timestamp = convert_seconds_to_srt_timestamp(end_time)

#             srt_file.write(f"{i+1}\n")
#             srt_file.write(f"{start_timestamp} --> {end_timestamp}\n")
#             srt_file.write(f"{text}\n\n")


# def convert_seconds_to_srt_timestamp(seconds):
#     milliseconds = int((seconds % 1) * 1000)
#     seconds = int(seconds)
#     minutes = seconds // 60
#     seconds = seconds % 60
#     hours = minutes // 60
#     minutes = minutes % 60
#     return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# def translate_text(text, dest_language):
#     try:
#         translated = GoogleTranslator(source="auto", target=dest_language).translate(
#             text
#         )
#         return translated
#     except Exception as e:
#         st.error(f"Error translating text: {text}\nError: {e}")
#         return text


# def read_srt_file(srt_file):
#     with open(srt_file, "r") as file:
#         content = file.read()

#     subtitles = re.split(r"\n\n", content)

#     parsed_subtitles = []
#     for subtitle in subtitles:
#         match = re.match(
#             r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.+)",
#             subtitle,
#             re.DOTALL,
#         )
#         if match:
#             index = match.group(1)
#             timing = match.group(2)
#             text = match.group(3).replace("\n", " ")
#             parsed_subtitles.append((index, timing, text))

#     return parsed_subtitles


# def translate_srt(srt_file, dest_language, output_file="translated_subtitles.srt"):
#     subtitles = read_srt_file(srt_file)

#     translated_subtitles = []
#     for index, timing, text in subtitles:
#         translated_text = translate_text(text, dest_language)
#         translated_subtitles.append(f"{index}\n{timing}\n{translated_text}\n")

#     with open(output_file, "w",encoding='utf-8') as file:
#         file.write("\n".join(translated_subtitles))


# def embed_subtitles(
#     video_input, subtitle_input, output_video="output_video_with_subtitles.mp4"
# ):
#     subtitle_filter = f"subtitles={subtitle_input}"
#     ffmpeg.input(video_input).output(output_video, vf=subtitle_filter).run()
#     return output_video


# def main():
#     languages_supported = {"Malayalam":"ml", "Telugu":"hi", "Hindi":"hi"}
#     st.title("Video CC translation app")

#     video_url = st.text_input(
#         "Enter YouTube Video URL",
#         placeholder="Please enter a valid YouTube video URL...",
#     )
#     selected_language = st.selectbox(
#         "Select your target language to transcribe the captions.",
#         tuple(languages_supported.keys()),
#     )
#     dest_language = languages_supported[selected_language]
#     if st.button("Process Video"):
#         if video_url and dest_language:
#             cwd = os.getcwd()
#             files = os.listdir(cwd)
#             for file in files:
#                 if file.startswith('processed_'):
#                     os.remove(os.path.join(cwd, file))
#             with st.spinner("Downloading video..."):
#                 video_file = download_video(video_url)

#             st.success("Video downloaded successfully!")

#             with st.spinner("Extracting audio..."):
#                 audio_file = extract_audio(video_file)

#             st.success("Audio extracted successfully!")

#             with st.spinner("Generating subtitles..."):
#                 segments = generate_subtitles(audio_file)
#                 srt_file = "whisper_output_subtitles.srt"
#                 save_transcript_to_srt(segments, srt_file)

#             st.success("Subtitles generated successfully!")

#             with st.spinner("Translating subtitles..."):
#                 translated_srt_file = "translated_subtitles.srt"
#                 translate_srt(srt_file, dest_language, translated_srt_file)

#             st.success("Subtitles translated successfully!")

#             with st.spinner("Embedding subtitles into video..."):
#                 output_video = embed_subtitles(video_file, translated_srt_file)

#             st.success(
#                 f"Subtitles embedded successfully! Final video saved as {output_video}"
#             )

#             st.video(output_video)
#         else:
#             st.error("Please provide a valid video URL and destination language.")


# if __name__ == "__main__":
#     main()


import streamlit as st
from yt_dlp import YoutubeDL
import whisper
from moviepy.editor import VideoFileClip
import ffmpeg
import os
from deep_translator import GoogleTranslator
import re
import uuid


def load_css(file_name="static/style.css"):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# def download_video(video_url):
#     ydl_opts = {
#         "format": "best",
#         "outtmpl": "input_video.%(ext)s",
#     }
#     with YoutubeDL(ydl_opts) as ydl:
#         result = ydl.extract_info(video_url, download=True)
#         return ydl.prepare_filename(result)

cookie_file = "cookies.txt"

def download_video(video_url, cookie_file=None, proxy=None):
    ydl_opts = {
        "format": "best",
        "outtmpl": "input_video.%(ext)s",
        "noplaylist": True,  # Prevents downloading entire playlists if the URL is part of one
        "nocheckcertificate": True,  # Avoid certificate errors
    }

    # Add cookies if provided
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
    with open(output_srt, "w") as srt_file:
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
    with open(srt_file, "r") as file:
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


def embed_subtitles(video_input, subtitle_input, output_video="final_video.mp4"):
    subtitle_filter = f"subtitles={subtitle_input}:force_style='FontName=Arial'"
    ffmpeg.input(video_input).output(output_video, vf=subtitle_filter).run()
    return output_video


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

    st.markdown('<p class="small-font" style="color:black;">**Only English videos supported as input</p>', unsafe_allow_html=True)
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

            with st.spinner("Generating subtitles..."):
                segments = generate_subtitles(audio_file)
                srt_file = "input_srt.srt"
                save_transcript_to_srt(segments, srt_file)

            st.success("Subtitles generated successfully!")

            with st.spinner("Translating subtitles..."):
                translated_srt_file = "translated_srt.srt"
                translate_srt(srt_file, dest_language, translated_srt_file)

            st.success("Subtitles translated successfully!")

            with st.spinner("Embedding subtitles into video..."):
                output_video = embed_subtitles(video_file, translated_srt_file)

            st.success(
                f"Subtitles embedded successfully!"
            )

            st.video(output_video)
        else:
            st.error("Please provide a valid video URL and destination language.")


if __name__ == "__main__":
    main()

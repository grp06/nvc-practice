import streamlit as st
from openai import OpenAI
import os
from audiorecorder import audiorecorder
import io

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=api_key)

def get_ai_response(scenario):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "The user is going to give you a scenario to practice non-violent communication. When they give you the scenario, your only job is to respond with a single statement or accusation from the other party. It should be moderly inflammatory. The user will then reply to it. Dont put it in quotes."},
            {"role": "user", "content": scenario}
        ]
    )
    return response.choices[0].message.content

def transcribe_audio(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text

def get_feedback(initial_prompt, user_response):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "The user is roleplaying a non-violent communication game."},
            {"role": "user", "content": f"The initial prompt is '{initial_prompt}' and the user responded this: '{user_response}'. Give feedback"}
        ]
    )
    return response.choices[0].message.content

def main():
    st.title("Scenario Input App")

    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None

    st.text("Enter a scenario")
    scenario = st.text_input("Scenario", key="scenario_input", label_visibility="collapsed")

    if st.button("Submit Scenario"):
        if scenario:
            with st.spinner("Processing..."):
                st.session_state.ai_response = get_ai_response(scenario)
        else:
            st.warning("Please enter a scenario before submitting.")

    if st.session_state.ai_response:
        st.write("Respond to this:")
        st.write(st.session_state.ai_response)
        
        audio = audiorecorder("Start Recording", "Stop Recording")
        
        if len(audio) > 0:
            audio_file = io.BytesIO(audio.export().read())
            audio_file.name = "recording.wav"

            with st.spinner("Transcribing..."):
                transcription = transcribe_audio(audio_file)
            
            st.write("Transcription:")
            st.write(transcription)

            with st.spinner("Getting feedback..."):
                feedback = get_feedback(st.session_state.ai_response, transcription)
            
            st.write("Feedback:")
            st.write(feedback)

if __name__ == "__main__":
    main()
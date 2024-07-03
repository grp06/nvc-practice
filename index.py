import streamlit as st
from openai import OpenAI
import os
from audiorecorder import audiorecorder
import io



def transcribe_audio(audio_file, client):
    # Add 'client' parameter
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text

def get_feedback(scenario, user_response, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "The user is roleplaying a non-violent communication game. They will provide a scenario and their response. Provide feedback on their response."},
            {"role": "user", "content": f"""Scenario: {scenario}\nUser's response: {user_response}

You must start your response with a score 1-10. 1 being the worst, 10 being the best.

Then give a detailed explanation of why you gave that score. Don't explain what NVC is just give me a score and an explanation.

Finally, I want you to give an "optimal" response. For this last segment, only write out the optimal response.
"""}
        ]
    )
    return response.choices[0].message.content

def main():
    st.title("Non-Violent Communication Practice")

    if 'api_key' not in st.session_state:
        st.session_state.api_key = None

    if not st.session_state.api_key:
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if st.button("Submit API Key"):
            if api_key:
                st.session_state.api_key = api_key
                st.experimental_rerun()
            else:
                st.warning("Please enter an API key.")
        return

    client = OpenAI(api_key=st.session_state.api_key)

    st.text("Type in a scenario. Like, 'My mom said, you never listen to me")
    scenario = st.text_input("Scenario", key="scenario_input", label_visibility="collapsed")

    audio = audiorecorder("Start Recording", "Stop Recording")
    
    if len(audio) > 0:
        audio_file = io.BytesIO(audio.export().read())
        audio_file.name = "recording.wav"

        with st.spinner("Transcribing..."):
            transcription = transcribe_audio(audio_file, client)
        
        st.write("Transcription:")
        st.write(transcription)

        with st.spinner("Getting feedback..."):
            feedback = get_feedback(scenario, transcription, client)
        
        st.write("Feedback:")
        st.write(feedback)

if __name__ == "__main__":
    main()
import streamlit as st
from openai import OpenAI
import os
from audiorecorder import audiorecorder
import io
from streamlit_javascript import st_javascript



def transcribe_audio(audio_file, client):
    # Add 'client' parameter
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text

def get_feedback(scenario, user_response, client):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in Non-Violent Communication (NVC) tasked with evaluating and providing feedback on user responses in various scenarios."},
            {"role": "user", "content": f"""Scenario: {scenario}
User's response: {user_response}

Evaluate the user's response based on Non-Violent Communication principles. Provide your feedback in the following format:

1. Score (1-100):
[Give a score from 1 to 100, where 1 is the least aligned with NVC principles and 100 is perfectly aligned]

2. Explanation:
[Provide a detailed explanation of the score, highlighting areas for improvement in the user's response]

3. Optimal NVC Response:
[Provide an example of an optimal response using NVC principles for this scenario]

Respond as Marshall Rosenberg, adhering strictly to the rules on non-violent communication.
"""}
        ]
    )
    return response.choices[0].message.content

def get_api_key_from_local_storage():
    return st.session_state.get('openai_api_key')

def save_api_key_to_local_storage(api_key):
    st.session_state['openai_api_key'] = api_key

def main():
    st.title("Non-Violent Communication Practice")

    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = None
    
    if 'refresh_counter' not in st.session_state:
        st.session_state.refresh_counter = 0

    if not st.session_state.openai_api_key:
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if st.button("Submit API Key"):
            if api_key:
                save_api_key_to_local_storage(api_key)
                st.experimental_rerun()
            else:
                st.warning("Please enter an API key.")
        return

    client = OpenAI(api_key=st.session_state.openai_api_key)

    if st.button("Refresh"):
        for key in list(st.session_state.keys()):
            if key not in ['openai_api_key', 'refresh_counter']:
                del st.session_state[key]
        st.session_state.refresh_counter += 1
        st.cache_data.clear()
        st.cache_resource.clear()
        st.experimental_rerun()

    st.text("Type in a scenario. Like, 'My mom said, you never listen to me")
    scenario = st.text_input("Scenario", key="scenario_input", label_visibility="collapsed")

    audio = audiorecorder("Start Recording", "Stop Recording", key=f"audio_{st.session_state.refresh_counter}")
    
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
import os
import pygame
from openai import OpenAI
from dotenv import load_dotenv

class VoiceEffectsManager:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.voice_mappings = {
            'sleep': 'shimmer',
            'study': 'onyx',
            'vent': 'nova'
        }
        
        self.pattern_data = {
            'peaks': [],
            'intensities': [],
            'duration': 0
        }
        pygame.mixer.init(44100, -16, 2, 1024)

    def record_pattern_data(self, audio_data, elapsed_time):
        self.pattern_data['peaks'].append(audio_data['has_recent_peak'])
        self.pattern_data['intensities'].append(audio_data['intensity'])
        self.pattern_data['duration'] = elapsed_time

    def generate_pattern_interpretation(self, category):
        try:
            peak_frequency = sum(self.pattern_data['peaks']) / max(len(self.pattern_data['peaks']), 1)
            avg_intensity = sum(self.pattern_data['intensities']) / max(len(self.pattern_data['intensities']), 1)
            duration_minutes = self.pattern_data['duration'] / 60
            
            prompts = {
                'sleep': f"As a sleep meditation guide, analyze this {duration_minutes:.1f} minute session with {peak_frequency:.1%} peak frequency and {avg_intensity:.1%} average intensity. Provide a brief, calming interpretation.",
                'study': f"As a study focus advisor, analyze this {duration_minutes:.1f} minute session with {peak_frequency:.1%} peak frequency and {avg_intensity:.1%} average intensity. Provide a brief, constructive interpretation.",
                'vent': f"As an empathetic listener, reflect on this {duration_minutes:.1f} minute emotional expression session with {peak_frequency:.1%} peak frequency and {avg_intensity:.1%} average intensity. Provide a brief, understanding interpretation."
            }
            
            # Get text interpretation
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a specialized pattern interpreter for audio visualization sessions."},
                    {"role": "user", "content": prompts[category]}
                ],
                max_tokens=150,
                temperature=0.7
            )
            interpretation = response.choices[0].message.content
            
            # Generate speech
            speech_file = "temp_speech.mp3"
            speech_response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice_mappings[category],
                input=interpretation
            )
            speech_response.stream_to_file(speech_file)
            
            # Play audio
            pygame.mixer.music.load(speech_file)
            pygame.mixer.music.play()
            
            # Delete temporary file after a delay
            pygame.time.delay(100)  # Small delay to ensure file is loaded
            os.remove(speech_file)
            
            return interpretation

        except Exception as e:
            print(f"Error generating interpretation: {e}")
            return "Unable to generate interpretation at this time."

    def reset_session(self):
        self.pattern_data = {
            'peaks': [],
            'intensities': [],
            'duration': 0
        }

    def get_voice(self, category):
        return self.voice_mappings.get(category, 'nova')
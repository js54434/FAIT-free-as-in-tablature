import pyaudio
import wave

# this should have anything we need open ahead of time
class AudioPlayer:
    def __init__(self):
        self.chunk = 1024
#        self.p = pyaudio.PyAudio()
        
        
class Playback:
    def __init__(self, parent):
        self._parent = parent
        self.audioPlayer = self._parent.audioPlayer
#        self.cursorItem = self._parent.cursorItem
        self.tracks = self._parent.tracks
        self.tempo = self._parent.midiPlayer.tempo
        
        self.chunk = 1024

        # for now, just open some random file
        self.f = wave.open(r"testSound.wav", "rb")
        
        self.p = pyaudio.PyAudio()
        
        self.stream = self.p.open(format = self.p.get_format_from_width(self.f.getsampwidth()),
                                channels = self.f.getnchannels(),
                                rate = self.f.getframerate(),
                                output = True)
                                
        data = self.f.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.f.readframes(self.chunk)
            
        self.stream.stop_stream()
        self.stream.close()
        
        self.f.close()
        
        self.p.terminate()

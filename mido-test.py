from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage, bpm2tempo
from enum import Enum
import opensimplex

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

class NoteType(Enum):
    SIXTEENTH = 0.25
    EIGHTH = 0.5
    QUARTER = 1
    HALF = 2
    WHOLE = 4  

pentatonic = [36, 38, 41, 43, 45] # Notes of the pentatonic scale on the first octave
whole_tone = [36, 38, 40, 42, 44, 46] # ^ but for whole tone scale

def get_note(note_type, ticks_per_beat, time_sig_denominator):
    return int(note_type.value * (time_sig_denominator / 4) * ticks_per_beat)

def append_to_track(note_pitch, velocity, start_time, note_type, ticks_per_beat, time_sig_denominator, track):
    end_time = get_note(note_type, ticks_per_beat, time_sig_denominator)
    track.append(Message('note_on', note=note_pitch, velocity=velocity, time=start_time))
    track.append(Message('note_off', note=note_pitch, velocity=velocity, time=end_time))
    return end_time

def get_note_in_scale(curr_note, scale):
    note_octave = curr_note // 12
    first_octave_note = (curr_note % 12) + 36
    
    closest_note = scale[0]
    for note in scale:
        if abs(first_octave_note - note) < abs(first_octave_note - closest_note):
            closest_note = note

    return closest_note + 12 * (note_octave - 3)

def get_note_type(time_sig_numerator):
    

def create_music(time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale, track, mid):
    while mid.length < time_duration:
        curr_note = int((opensimplex.noise2(mid.length * 4, 1) + 1) / 2 * (96 - 36) +  36)
        curr_note_type = get_note_type()
        append_to_track(get_note_in_scale(curr_note, scale), 64, 0, NoteType.SIXTEENTH, mid.ticks_per_beat, time_sig_denominator, track)        

def create_midi(bpm, scale, time_sig_numerator, time_sig_denominator):
    mid = MidiFile(type=1)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('time_signature', numerator=time_sig_numerator, denominator=time_sig_denominator))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    create_music(20, 0, time_sig_numerator, time_sig_denominator, scale, track, mid)


    mid.save('./midi-gen/new_song.mid')
    return mid


opensimplex.seed(1233)
mid = create_midi(240, whole_tone, 4, 4)
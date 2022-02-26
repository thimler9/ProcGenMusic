import os
import random
from turtle import pos
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

def get_note_type(beats_left_in_measure, curr_time_in_song):
    note_types = [e for e in NoteType]
    possible_note_types = []
    for i in range(len(note_types)):
        if note_types[i].value <= beats_left_in_measure:
            possible_note_types.append(note_types[i])
    return possible_note_types[int((opensimplex.noise2(curr_time_in_song * 2, 1) + 1) / 2 * (len(possible_note_types)))]


def create_music(time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale, track, mid):
    beats_left_in_measure = float(time_sig_numerator)
    # Generates a note per iteration
    while mid.length < time_duration:
        curr_note = int((opensimplex.noise2(mid.length * 2, 1) + 1) / 2 * (96 - 36) +  36)
        curr_note_type = get_note_type(beats_left_in_measure, mid.length)
        beats_left_in_measure -= curr_note_type.value
        if beats_left_in_measure <= 0:
            beats_left_in_measure = float(time_sig_numerator)
        append_to_track(get_note_in_scale(curr_note, scale), 64, 0, curr_note_type, mid.ticks_per_beat, time_sig_denominator, track)

def create_rhythm(time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale, track, mid):
    beats_left_in_measure = float(time_sig_numerator)
    velocity = 64
    # Generates a note per iteration
    while mid.length < time_duration:
        curr_note = int((opensimplex.noise2(mid.length * 2, 1) + 1) / 2 * (96 - 36) +  36)
        curr_note_type = get_note_type(beats_left_in_measure, mid.length)
        beats_left_in_measure -= curr_note_type.value
        if beats_left_in_measure <= 0:
            beats_left_in_measure = float(time_sig_numerator)
            velocity = int((opensimplex.noise2(mid.length * 2, 10) + 1) / 2 * (104 - 84) +  64)
        else:
            velocity = int((opensimplex.noise2(mid.length * 2, 10) + 1) / 2 * (74 - 54) +  64)
        append_to_track(get_note_in_scale(curr_note, scale), velocity, 0, curr_note_type, mid.ticks_per_beat, time_sig_denominator, track)

def create_midi(bpm, scale, time_sig_numerator, time_sig_denominator, seed):
    opensimplex.seed(seed)
    mid = MidiFile(type=1)
    melody = MidiTrack()
    bass = MidiTrack()
    mid.tracks.append(melody)
    mid.tracks.append(bass)
    
    melody.append(Message('program_change', program=4, time=0))
    melody.append(MetaMessage('time_signature', numerator=time_sig_numerator, denominator=time_sig_denominator))
    melody.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    bass.append(Message('program_change', program=36, time=0))
    bass.append(MetaMessage('time_signature', numerator=time_sig_numerator, denominator=time_sig_denominator))
    bass.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    create_music(20, 0, time_sig_numerator, time_sig_denominator, scale, melody, mid)
    create_rhythm(20, 0, time_sig_numerator, time_sig_denominator, scale, bass, mid)

    mid.save('./midi-gen/' + str(seed) + '.mid')
    return mid


mid = create_midi(240, pentatonic, 3, 4, 666)
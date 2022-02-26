import random
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage, bpm2tempo
from enum import Enum
import opensimplex
import math

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

class NoteType(Enum):
    SIXTEENTH = 0.25
    EIGHTH = 0.5
    QUARTER = 1
    HALF = 2
    WHOLE = 4

class KeySignature(Enum):
    C = 0
    CSHARP = 1
    D = 2
    DSHARP = 3
    E = 4
    F = 5
    FSHARP = 6
    G = 7
    GSHARP = 8
    A = 9
    ASHARP = 10
    B = 11

class Scale(Enum):
    PENTATONIC = [36, 38, 41, 43, 45] # Notes of the pentatonic scale on the first octave
    WHOLE_TONE = [36, 38, 40, 42, 44, 46] # ^ but for whole tone scale
    MAJOR = [36, 38, 40, 41, 43, 45, 47]

def get_note(note_type, ticks_per_beat, time_sig_denominator):
    return int(note_type.value * (time_sig_denominator / 4) * ticks_per_beat)

def append_to_track(note_pitch, velocity, note_type, ticks_per_beat, time_sig_denominator, track):
    end_time = get_note(note_type, ticks_per_beat, time_sig_denominator)
    track.append(Message('note_on', note=note_pitch, velocity=velocity, time=0))
    track.append(Message('note_off', note=note_pitch, velocity=velocity, time=end_time))
    return end_time

def get_note_in_scale(curr_note, scale, key_signature):
    note_octave = curr_note // 12
    first_octave_note = (curr_note % 12) + 36
    
    closest_note = scale[0]
    for note in scale:
        if abs(first_octave_note - note) < abs(first_octave_note - closest_note):
            closest_note = note
        if abs(first_octave_note - note) == abs(first_octave_note - closest_note):
            if random.randint(0, 1) == 0:
                closest_note = note

    return closest_note + 12 * (note_octave - 3) + key_signature.value

def get_note_type(note_types, beats_left_in_measure, curr_time_in_song):
    possible_note_types = []
    for i in range(len(note_types)):
        if note_types[i].value <= beats_left_in_measure:
            possible_note_types.append(note_types[i])
    return possible_note_types[int((opensimplex.noise2(curr_time_in_song * 2, 1) + 1) / 2 * (len(possible_note_types)))]


def create_music(time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale, track, mid):
    beats_left_in_measure = float(time_sig_numerator)

    curr_velocity = 0
    number_of_rests_skipped = 0

    # Generates a note per iteration
    while mid.length < time_duration:
        curr_note = int((opensimplex.noise2(mid.length * 2, 1) + 1) / 2 * 60 +  36)
        curr_note_type = get_note_type([e for e in NoteType], beats_left_in_measure, mid.length)
        beats_left_in_measure -= curr_note_type.value
        if beats_left_in_measure <= 0:
            beats_left_in_measure = float(time_sig_numerator)

        if random.random() - 0.05 * number_of_rests_skipped > 0.75:
            curr_velocity = 0
            number_of_rests_skipped += 1
        else:
            curr_velocity = 80
            number_of_rests_skipped = 0
        
        append_to_track(get_note_in_scale(curr_note, scale, key_signature), curr_velocity, curr_note_type, mid.ticks_per_beat, time_sig_denominator, track)

def generate_measure(time_sig_numerator, measure_number, mid):
    beats_left_in_measure = float(time_sig_numerator)
    measure = []
    types = [NoteType.HALF, NoteType.QUARTER, NoteType.EIGHTH]

    curr_velocity = 0
    number_of_rests_skipped = 0

    while beats_left_in_measure > 0:
        curr_note = int((opensimplex.noise2(beats_left_in_measure, measure_number * 100) + 1) / 2 * 60 +  36)
        curr_note_type = get_note_type(types, beats_left_in_measure, mid.length)
        if beats_left_in_measure == float(time_sig_numerator) or beats_left_in_measure == float(math.ceil(time_sig_numerator / 2)):
            curr_velocity = int((opensimplex.noise2(beats_left_in_measure, measure_number * 1000) + 1) / 2 * 10 + 50)
        else:
            if random.random() - 0.05 * number_of_rests_skipped > 0.75:
                curr_velocity = 0
                number_of_rests_skipped += 1
            else:
                curr_velocity = int((opensimplex.noise2(beats_left_in_measure, measure_number * 2000) + 1) / 2 * 30 + 25)
                number_of_rests_skipped = 0    
        
        
        beats_left_in_measure -= curr_note_type.value
        measure.append((curr_note, curr_velocity, curr_note_type))
    return measure

def create_rhythm(measure_count, time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale, track, mid):
    measures = []
    for i in range(measure_count):
        measures.append(generate_measure(time_sig_numerator, i, mid))
    
    while mid.length < time_duration:
        for measure in measures:
            for note in measure:
                (note_pitch, velocity, note_type) = note
                append_to_track(get_note_in_scale(note_pitch, scale, key_signature), velocity, note_type, mid.ticks_per_beat, time_sig_denominator, track)

def create_midi(bpm, scale, key_signature, time_sig_numerator, time_sig_denominator, seed):
    opensimplex.seed(seed)
    mid = MidiFile(type=1)
    melody = MidiTrack()
    bass = MidiTrack()

    
    melody.append(Message('program_change', program=4, time=0))
    melody.append(MetaMessage('time_signature', numerator=time_sig_numerator, denominator=time_sig_denominator))
    melody.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    bass.append(Message('program_change', program=36, time=0))
    bass.append(MetaMessage('time_signature', numerator=time_sig_numerator, denominator=time_sig_denominator))
    bass.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))

    time_duration = 20

    mid.tracks.append(melody)
    create_music(time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale.value, melody, mid)
    mid.tracks.pop()
    mid.tracks.append(bass)
    create_rhythm(2, time_duration, key_signature, time_sig_numerator, time_sig_denominator, scale.value, bass, mid)
    mid.tracks.pop()

    mid.tracks.append(melody)
    mid.tracks.append(bass)
    mid.save('./midi-gen/' + scale.name + str(seed) + key_signature.name + '.mid')

    return mid


create_midi(120, Scale.MAJOR, KeySignature.A, 3, 4, 69420)

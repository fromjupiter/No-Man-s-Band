import librosa
import pretty_midi
import ext.interpreter as itp
import jams
import os
import logging
from PIL import Image
import numpy as np


def piano_roll_to_pretty_midi(piano_roll, fs=100, program=0):
    '''Convert a Piano Roll array into a PrettyMidi object
     with a single instrument.
    Parameters
    ----------
    piano_roll : np.ndarray, shape=(128,frames), dtype=int
        Piano roll of one instrument
    fs : int
        Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    program : int
        The program number of the instrument.
    Returns
    -------
    midi_object : pretty_midi.PrettyMIDI
        A pretty_midi.PrettyMIDI class instance describing
        the piano roll.
    '''
    notes, frames = piano_roll.shape
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    # pad 1 column of zeros so we can acknowledge inital and ending events
    piano_roll = np.pad(piano_roll, [(0, 0), (1, 1)], 'constant')

    # use changes in velocities to find note on / note off events
    velocity_changes = np.nonzero(np.diff(piano_roll).T)

    # keep track on velocities and note on times
    prev_velocities = np.zeros(notes, dtype=int)
    note_on_time = np.zeros(notes)

    for time, note in zip(*velocity_changes):
        # use time + 1 because of padding above
        velocity = piano_roll[note, time + 1]
        time = time / fs
        if velocity > 0:
            if prev_velocities[note] == 0:
                note_on_time[note] = time
                prev_velocities[note] = velocity
        else:
            pm_note = pretty_midi.Note(
                velocity=prev_velocities[note],
                pitch=note,
                start=note_on_time[note],
                end=time)
            instrument.notes.append(pm_note)
            prev_velocities[note] = 0
    pm.instruments.append(instrument)
    return pm

def jams_to_piano_roll(jam, unit=24):
    midi = itp.jams_to_midi(jam, q=0)
    # get tempo
    annos = jam.search(namespace='tempo')
    bpm = None
    for anno in annos:
        for tempo in anno:
            bpm = tempo.value
    if bpm is None:
        logging.warning("Tempo not found in jams, using 120 as default.")
        bpm = 120
    fs = unit*bpm/60
    roll = midi.get_piano_roll(fs=fs)
    new_midi = piano_roll_to_pretty_midi(roll, fs = fs)
    new_midi.write('test.midi')
    return roll


if __name__=='__main__':
    gs_path = "e:/workspace/guitar_set/"
    anno_dir = "annotation/"
    # excerpt = "05_Jazz2-187-F#_comp.jams"
    excerpt = "00_Rock1-90-C#_comp.jams"
    jam = jams.load(os.path.join(gs_path+anno_dir, excerpt))
    roll = jams_to_piano_roll(jam)
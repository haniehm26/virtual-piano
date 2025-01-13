import rtmidi
import sys
from constants import NOTE_VELOCITY


def initialize_midi():
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    if available_ports:
        midiout.open_port(0)
    else:
        sys.exit(1)
    return midiout

def note_on(midiout, note):
    midiout.send_message([0x90, note, NOTE_VELOCITY])

def note_off(midiout, note):
    midiout.send_message([0x80, note, 0])

import os
from nose.tools import assert_equal

from instrument import Instrument
from project import load_lsdsng

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

def test_load_lsdinst():
    proj = load_lsdsng(os.path.join(SCRIPT_DIR, 'test_data', 'UNTOLDST.lsdsng'))

    proj.song.instruments.import_from_file(
        0x2a,
        os.path.join(SCRIPT_DIR, 'test_data', 'KI.lsdinst'))

    target_instr = proj.song.instruments[0x2a]

    assert_equal('wave', target_instr.type)

    # Should have allocated a new synth in slot 2
    synth = target_instr.synth

    assert_equal(2, synth.index)
    assert_equal('KI\0\0\0', target_instr.name)
    assert_equal('wave', target_instr.type)
    assert_equal(3, target_instr.volume)
    assert_equal(0, target_instr.repeat)
    assert_equal('allpass', synth.filter_type)
    assert_equal('clip', synth.distortion)
    assert_equal(3, synth.filter_resonance)
    assert_equal(144, synth.end.volume)
    assert_equal(97, synth.start.volume)
    assert_equal(118, synth.start.filter_cutoff)

    assert_equal([8, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 12, 15,
                  15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 12],
                 synth.waves[1])

    assert_equal('P', target_instr.table.fx1[0].command)
    assert_equal('K', target_instr.table.fx1[6].command)

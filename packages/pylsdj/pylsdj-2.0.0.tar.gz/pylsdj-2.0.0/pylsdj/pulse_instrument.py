from instrument import Instrument
from bread_spec import INSTRUMENT_TYPE_CODE
from instrument_mixins import EnvelopeMixin, SoundLengthMixin, VibratoMixin, \
    SweepMixin

MIXINS = [VibratoMixin, SoundLengthMixin, EnvelopeMixin, SweepMixin]

class PulseInstrument(Instrument,
                      VibratoMixin, SoundLengthMixin, EnvelopeMixin,
                      SweepMixin):
    def __init__(self, song, index):
        super(PulseInstrument, self).__init__(song, index)

    @property
    def phase_transpose(self):
        """detune pulse channel 2 this many semitones; in LSDJ, this is
        ``PU2 TUNE`` (8-bit integer)"""
        return self.data.phase_transpose

    @phase_transpose.setter
    def phase_transpose(self, value):
        self.data.phase_transpose = value

    @property
    def phase_finetune(self):
        """detune pulse channel 1 down, channel 2 up; in LSDJ, this is
        ``PU FINE`` (4-bit integer)"""
        return self.data.phase_finetune

    @phase_finetune.setter
    def phase_finetune(self, value):
        self.data.phase_finetune = value

    @property
    def wave(self):
        """the pulse's wave width; ``12.5%``, ``25%``, ``50%`` or ``75%``"""
        return self.data.wave

    @wave.setter
    def wave(self, value):
        self.data.wave = value

    def import_lsdinst(self, struct_data):
        super(PulseInstrument, self).import_lsdinst(struct_data)

        self.phase_transpose = struct_data['data']['phase_transpose']
        self.phase_finetune = struct_data['data']['phase_finetune']
        self.wave = struct_data['data']['wave']

        for mixin in MIXINS:
            mixin.import_from_struct_data(self, struct_data)

from utils import assert_index_sane
import json


class Instrument(object):

    def __init__(self, song, index):
        self.song = song
        self.data = song.song_data.instruments[index]
        self.index = index

    def __eq__(self, other):
        return (isinstance(other, Instrument) and
                self.name == other.name and
                self.type == other.type and
                self.table == other.table and
                self.automate == other.automate and
                self.pan == other.pan)

    @property
    def name(self):
        """the instrument's name (5 characters, zero-padded)"""
        return self.song.song_data.instrument_names[self.index]

    @name.setter
    def name(self, val):
        self.song.song_data.instrument_names[self.index] = val

    @property
    def type(self):
        """the instrument's type (``pulse``, ``wave``, ``kit`` or ``noise``)"""
        return self.data.instrument_type

    @property
    def table(self):
        """a ```pylsdj.Table``` referencing the instrument's table, or None
        if the instrument doesn't have a table"""
        if hasattr(self.data, 'table_on') and self.data.table_on:
            assert_index_sane(self.data.table, len(self.song.tables))
            return self.song.tables[self.data.table]

    @table.setter
    def table(self, value):
        if not hasattr(self.data, "table_on"):
            raise ValueError("This instrument doesn't have a table")

        self.data.table_on = True
        self.data.table = value.index

    @property
    def automate(self):
        """if True, automation is on"""
        return self.data.automate

    @automate.setter
    def automate(self, value):
        self.data.automate = value

    @property
    def pan(self):
        return self.data.pan

    @pan.setter
    def pan(self, value):
        self.data.pan = value

    def import_lsdinst(self, struct_data):
        """import from an lsdinst struct"""
        self.name = struct_data['name']
        self.automate = struct_data['data']['automate']
        self.pan = struct_data['data']['pan']

        if self.table is not None:
            self.table.import_lsdinst(struct_data)

    def export_to_file(self, filename):
        """Export this instrument's settings to a file.

        :param filename: the name of the file
        """
        instr_json = self.export_struct()

        with open(filename, 'w') as fp:
            json.dump(instr_json, fp, indent=2)

    def export_struct(self):
        export_struct = {}

        export_struct['name'] = self.name
        export_struct['data'] = {}

        data_json = json.loads(self.data.as_json())

        for key, value in data_json.items():
            if key[0] != '_' and key not in ('synth', 'table'):
                export_struct['data'][key] = value

        if self.table is not None:
            export_struct['table'] = self.table.export()

        return export_struct

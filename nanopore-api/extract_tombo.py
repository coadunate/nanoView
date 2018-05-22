""" Basic Program for extracing time and signal values for given event ranges.
"""

import h5py # for File
import os
from ont_fast5_api.fast5_info import Fast5Info # for Fast5Info
import re # regular expressions
import json # to parse event data
from SAMParse import *
import pandas as pd


class Fast5Events(object):
    """ This object is comprised of functions that can be performed on the event
        data of the given fast5 file.
    """

    def __init__(self,filename):
        """ Constructor. Opens the specified file
            :param filename: Filename to open
        """

        # Attributes Initializeation

        self.filename = filename
        self.handle = None
        self._is_open = False
        self.status = Fast5Info(self.filename)
        self.events = None


        if self.status.valid:
            self.handle = h5py.File(self.filename, 'r') # Open the file in read-only mode
            self._is_open = True


    def __enter__(self):
        return self

    def __exit__(self,exception_type,exception_value,traceback):
        self.close()
        return False


    def assert_open(self):
        if not self._is_open:
            raise IOError("Fast5 file is not open: {}".format(self.filename))

    def close(self):
        """ Closes the fast5 file that was opened by the object intitialization
        """

        if self._is_open:
            if self.handle:
                self.handle.close()
                self.handle = None
            self.filename = None
            self._is_open = False
            self.status = None

    def populate_events(self):
        """ Intelligently identifies the URL (within fast5 file) for Events dataset
            and extracts the events and saves it into the events field of this
            object
        """
        self.assert_open() # Throw an error if the fast5 file is not open

        # Determining the Events dataset
        all_objs = []  # Create a list of empty objects
        self.handle.visit(all_objs.append) # populate all_objs with the objecs in the fast5 file
        all_datasets = [ obj for obj in all_objs if isinstance(self.handle[obj],h5py.Dataset) ]
        # dataset_name = all_datasets[ [ i for i, dataset in enumerate(all_datasets) if dataset.endswith('Events') ][0] ] # events dataset
        dataset_name = '/Analyses/RawGenomeCorrected_000/BaseCalled_template/Events'
        self.events = self.handle[dataset_name] # get the events array from the events dataset

    def assert_events(self):
        self.populate_events()
        if self.events == None:
            raise IOError("The Event data isn't populated yet")

    def get_event_count(self):
        """ Returns an integer value representing the number of events
            that are present in the given fast5 file.
        """
        self.assert_events() # Throw an erorr if the event data isn't populated.

        return len(self.events);


    def get_event_time_data(self,event_start,event_end):
        """ Returns a list containing the event time values of the events from
            the given ranges of start and end events in the arguments
        """
        self.assert_events() # Throw an error if the event data isn't populated

        time_data = [] # Create empty list which will contain the time data

        time_index = self.get_start_time_index()

        for i in range(event_start,event_end):
            time_data.append(self.events[i][time_index])

        return time_data

    def get_event_signal_data(self,event_start,event_end):
        """ Returns a list containing the event signal values of the events from
            the given ranges of start and end events in the arguments
        """
        self.assert_events() # Throw an error if the event data isn't populated

        signal_data = [] # Create empty list which will contain the signal data

        signal_index = self.get_mean_signal_index()

        for i in range(event_start,event_end):
            signal_data.append(self.events[i][signal_index])

        return signal_data


    def get_set_event_signal_data(self,eventNumbers):
        """ Returns a list containing the event signal values of the events from
            the event numbers provided as arguments to this function
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        signal_data = [] # Create empty list which will contain the signal data

        signal_index = self.get_mean_signal_index()

        for i in range(len(eventNumbers)):
            signal_data.append(self.events[eventNumbers[i]][signal_index])

        return signal_data


    def map_bp_to_events(self,bp):
        """ Returns a list containing event numbers of the events that correspond
            to the given list of 5'mers as an argument
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        if not bp:
            raise IOError("The list of basepairs provided is not compatible.")


        model_index = self.get_model_state_index()

        bp_upperbound = len(bp) - 5
        retEventNumbers = [] # empty list that will contain the event numbers
        event_start = 0
        matches_so_far = 0
        for i in range(0,bp_upperbound+1): # loop through the base pairs
            if matches_so_far >= 2:
                break;
            while(event_start < len(self.events)):
                strbp = ''.join(bp[i:i+5])
                strevent = "".join( [ chr(item) for item in self.events[event_start][model_index] ])
                if(strbp == strevent):
                    retEventNumbers.append(event_start)
                    event_start = event_start + 1
                    matches_so_far = matches_so_far + 1
                    break
                event_start = event_start + 1

        if matches_so_far >= 2:
            while(event_start < len(self.events)):

                strbp = ''.join(bp[-5:])
                strevent = ''.join( [ chr(item) for item in self.events[event_start][model_index] ])
                if(strbp == strevent):
                    retEventNumbers.append(event_start)
                    break
                else:
                    event_start = event_start + 1
        return retEventNumbers


    def get_start_time_index(self):
        """ Returns an integer value representing the offset of the start time
            value of the event pore model
        """
        self.assert_events() # Throw an error if the event data isn't populated

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of start time value
        start_index = -1
        for index,field in enumerate(field_header_arr):
            if field == "start":
                start_index = index

        return start_index

    def get_move_index(self):
        """ Returns an integer value representing the move value
        """

        self.assert_events()

        field_header_arr = self.events.dtype.names

        move_index = -1
        for index, field in enumerate(field_header_arr):
            if field == "move":
                move_index = index

        return move_index

    def get_model_state_index(self):
        """ Returns an integer value representing the index of the model state
            of the given fast5 file.
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of model_state value
        model_index = -1
        for index,field in enumerate(field_header_arr):
            if field == "model_state":
                model_index = index
        return model_index

    def get_length_index(self):
        """ Returns an integer value representing the index of the length
            of the given fast5 file.
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of length value
        length_index = -1
        for index,field in enumerate(field_header_arr):
            if field == "length":
                length_index = index
        return length_index

    def get_mean_signal_index(self):
        """ Returns an integer value representing the offset of the mean signal
            value of the event pore model
        """
        self.assert_events() # Throw an error if the event data isn't populated

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of mean signal value
        mean_signal = -1
        for index,field in enumerate(field_header_arr):
            if field == "norm_mean":
                mean_signal = index
        return mean_signal

    def get_base_index(self):
        """ Returns an integer value representing the offset of the mean signal
            value of the event pore model
        """
        self.assert_events() # Throw an error if the event data isn't populated

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of mean signal value
        mean_signal = -1
        for index,field in enumerate(field_header_arr):
            if field == "base":
                mean_signal = index
        return mean_signal

    def get_qname(self):
        self.assert_events()

        qname_path = '/Analyses/Basecall_1D_000/BaseCalled_template/Fastq'
        dset = self.handle[qname_path]
        return dset.value.decode("utf-8").split('\n')[0][1:].split('_')[-2]


    def get_offset(self):
        self.assert_events()

        dset = '/Analyses/RawGenomeCorrected_000/BaseCalled_template/Events'
        dset = self.handle[dset]
        return dset.attrs['read_start_rel_to_raw']


    def get_mapped_start(self):
        self.assert_events()

        dset = '/Analyses/RawGenomeCorrected_000/BaseCalled_template/Alignment'
        dset = self.handle[dset]
        return dset.attrs['mapped_start']


    def get_base(self):
        self.assert_events()

        dset = '/Analyses/RawGenomeCorrected_000/BaseCalled_template/Events'
        dset = self.handle[dset]
        return dset['base']


    def get_list_event_data(self,event_start = -1, event_end = -1, file_path=""):
        signal_index = self.get_mean_signal_index()
        time_index = self.get_start_time_index()
        length_index = self.get_length_index()
        base = self.get_base_index()
        max_sig = 0
        min_sig = 100
        record = []
        qname = self.get_qname()
        # qname = qname.split('_')[-2]
        pos = get_pos_t(file_path, qname)
        offset = self.get_offset()
        # cigar_offsets_d = []
        # cigar_offsets_i = []
        cigar_offsets = []
        cigar = get_cigar_t(file_path, qname)
        for i in range(len(cigar)):
            if cigar[i] == 'd':
                cigar_offsets.append((i, 'd'))
            if cigar[i] == 'i':
                cigar_offsets.append((i, 'i'))
        record.append(qname)
        sub0 = []
        if event_start is -1 and event_end is -1:
            prev_move = -1
            # get all the events of a given fast5 file
            for i in range(0,self.get_event_count()):
                if self.events[i][signal_index] > max_sig:
                    max_sig = self.events[i][signal_index]
                if self.events[i][signal_index] < min_sig:
                    min_sig = self.events[i][signal_index]
                sub1 = []
                sub0.append(str(pos + i))
                sub1.append([str(i+pos), str(self.events[i][signal_index]),
                    str(self.events[i][time_index]),
                    str(self.events[i][length_index]), ""])
                sub0.append(sub1)
            max_min = []
            max_min.append(str(max_sig))
            max_min.append(str(min_sig))
            record.append(sub0)
            return record, max_min, cigar_offsets, pos

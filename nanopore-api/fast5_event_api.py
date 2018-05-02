""" Basic Program for extracing time and signal values for given event ranges.
"""

import h5py # for File
import os
from ont_fast5_api.fast5_info import Fast5Info # for Fast5Info
import re # regular expressions
import json # to parse event data


class Fast5Event(object):
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
        dataset_name = all_datasets[ [ i for i, dataset in enumerate(all_datasets) if dataset.endswith('Events') ][0] ] # events dataset
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

    # def get_json_event_data(self,event_start = -1, event_end = -1):
    #
    #     signal_index = self.get_mean_signal_index()
    #     time_index = self.get_start_time_index()
    #     model_index = self.get_model_state_index()
    #     length_index = self.get_length_index()
    #     stdv_index = self.get_stdv_index()
    #     move = self.get_move_index()
    #     record = ""
    #
    #     if event_start is -1 and event_end is -1:
    #         prev_move = -1
    #         # get all the events of a given fast5 file
    #         #print("index,signal,time,model,length,stdv")
    #         for i in range(0,self.get_event_count()):
    #             if(i == (self.get_event_count()-1)):
    #                 record = record + (
    #                     ",\n\t\t{\n" +
    #                     "\t\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                     "\t\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                     "\t\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                     "\t\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                     "\t\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                     "\t\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                     "\t\t}\n\t]\n}"
    #                 )
    #             else:
    #                 if prev_move == -1:
    #                     if self.events[i][move] == 1:
    #                         prev_move = 0
    #                     record = record + (
    #                         "{\n\t\"" + str(prev_move) + "\":\n\t[\n\t\t{\n"
    #                         "\t\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t\t}"
    #                     )
    #                 elif prev_move != -1 and self.events[i][move] == 0:
    #                     record = record + (
    #                         ",\n\t\t{\n" +
    #                         "\t\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t\t}"
    #                     )
    #                 elif prev_move != -1 and self.events[i][move] == 1:
    #                     prev_move += 1
    #                     record = record + (
    #                         "\n\t],\n\t\"" + str(prev_move) + "\":\n\t[\n\t\t{\n"
    #                         "\t\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t\t}"
    #                     )
    #
    #     elif event_end <= event_start:
    #         raise IOError("The start event should be less than end and there \
    #         should at least be one event")
    #     else:
    #         prev_move = -1
    #         # get only events from start to end
    #         # print("index,signal,time,model,length,stdv")
    #         for i in range(event_start,event_end):
    #
    #             if(i == (event_end-1)):
    #                 record = record + (
    #                     "\t{\n" +
    #                     "\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                     "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                     "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                     "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                     "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                     "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                     "\t\t}\n\t}"
    #                 )
    #             else:
    #                 if prev_move == -1 and self.events[i][move] == 1:
    #                     prev_move = 0
    #                     record = record + (
    #                         "},\n\t{\n\t\"" + str(prev_move) + "\":\n{\n"
    #                         "\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t}"
    #                     )
    #                 elif prev_move != -1 and self.events[i][move] == 0:
    #                     record = record + (
    #                         ",\n\t{\n" +
    #                         "\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t}"
    #                     )
    #                 elif prev_move != -1 and self.events[i][move] == 1:
    #                     prev_move += 1
    #                     record = record + (
    #                         "},\n\t{\n\t\"" + str(prev_move) + "\":\n{\n"
    #                         "\t\t\"index\": \"" + str(i+1) + "\",\n" +
    #                         "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
    #                         "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
    #                         "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
    #                         "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
    #                         "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
    #                         "\t}"
    #                     )
    #                     # print(record)
    #     # print(record)
    #     return record

    def get_json_event_data(self,event_start = -1, event_end = -1):

        signal_index = self.get_mean_signal_index()
        time_index = self.get_start_time_index()
        model_index = self.get_model_state_index()
        length_index = self.get_length_index()
        stdv_index = self.get_stdv_index()
        move = self.get_move_index()
        record = "{\"" + str(self.get_qname()) + "\": "

        if event_start is -1 and event_end is -1:
            prev_move = -1
            # get all the events of a given fast5 file
            #print("index,signal,time,model,length,stdv")
            for i in range(0,self.get_event_count()):
                if(i == (self.get_event_count()-1)):
                    record = record + (
                        ",{" +
                        "\"index\": \"" + str(i+1) + "\"," +
                        "\"signal\": \"" + str(self.events[i][signal_index]) + "\"," +
                        "\"time\": \"" + str(self.events[i][time_index]) + "\"," +
                        "\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + "," +
                        "\"length\": \"" + str(self.events[i][length_index]) + "\"," +
                        "\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"" +
                        "}]}"
                    )
                else:
                    if prev_move == -1:
                        if self.events[i][move] == 1:
                            prev_move = 0
                        record = record + (
                            "{\"" + str("%06d" % prev_move) + "\":[{"
                            "\"index\": \"" + str(i+1) + "\",\n" +
                            "\"signal\": \"" + str(self.events[i][signal_index]) + "\"," +
                            "\"time\": \"" + str(self.events[i][time_index]) + "\"," +
                            "\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + "," +
                            "\"length\": \"" + str(self.events[i][length_index]) + "\"," +
                            "\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"" +
                            "}"
                        )
                    elif prev_move != -1 and self.events[i][move] == 0:
                        record = record + (
                            ",{" +
                            "\"index\": \"" + str(i+1) + "\"," +
                            "\"signal\": \"" + str(self.events[i][signal_index]) + "\"," +
                            "\"time\": \"" + str(self.events[i][time_index]) + "\"," +
                            "\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + "," +
                            "\"length\": \"" + str(self.events[i][length_index]) + "\"," +
                            "\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"" +
                            "}"
                        )
                    elif prev_move != -1 and self.events[i][move] == 1:
                        prev_move += 1
                        record = record + (
                            "],\"" + str("%06d" % prev_move) + "\":[{"
                            "\"index\": \"" + str(i+1) + "\"," +
                            "\"signal\": \"" + str(self.events[i][signal_index]) + "\"," +
                            "\"time\": \"" + str(self.events[i][time_index]) + "\"," +
                            "\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + "," +
                            "\"length\": \"" + str(self.events[i][length_index]) + "\"," +
                            "\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"" +
                            "}"
                        )

        elif event_end <= event_start:
            raise IOError("The start event should be less than end and there \
            should at least be one event")
        else:
            prev_move = -1
            # get only events from start to end
            # print("index,signal,time,model,length,stdv")
            for i in range(event_start,event_end):

                if(i == (event_end-1)):
                    record = record + (
                        "\t{\n" +
                        "\t\t\"index\": \"" + str(i+1) + "\",\n" +
                        "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
                        "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
                        "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
                        "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
                        "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
                        "\t\t}\n\t}"
                    )
                else:
                    if prev_move == -1 and self.events[i][move] == 1:
                        prev_move = 0
                        record = record + (
                            "},\n\t{\n\t\"" + str(prev_move) + "\":\n{\n"
                            "\t\t\"index\": \"" + str(i+1) + "\",\n" +
                            "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
                            "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
                            "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
                            "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
                            "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
                            "\t}"
                        )
                    elif prev_move != -1 and self.events[i][move] == 0:
                        record = record + (
                            ",\n\t{\n" +
                            "\t\t\"index\": \"" + str(i+1) + "\",\n" +
                            "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
                            "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
                            "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
                            "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
                            "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
                            "\t}"
                        )
                    elif prev_move != -1 and self.events[i][move] == 1:
                        prev_move += 1
                        record = record + (
                            "},\n\t{\n\t\"" + str(prev_move) + "\":\n{\n"
                            "\t\t\"index\": \"" + str(i+1) + "\",\n" +
                            "\t\t\"signal\": \"" + str(self.events[i][signal_index]) + "\",\n" +
                            "\t\t\"time\": \"" + str(self.events[i][time_index]) + "\",\n" +
                            "\t\t\"model\": \"" + "".join( [ chr(item) for item in self.events[event_start][model_index] ]) + "\"" + ",\n" +
                            "\t\t\"length\": \"" + str(self.events[i][length_index]) + "\",\n" +
                            "\t\t\"stdv\": \"" + str(self.events[i][stdv_index]) + "\"\n" +
                            "\t}"
                        )
                        # print(record)
        # print(record)
        record = record + "}"
        return record

    def get_csv_event_data(self,event_start = -1, event_end = -1):

        signal_index = self.get_mean_signal_index()
        time_index = self.get_start_time_index()
        model_index = self.get_model_state_index()
        length_index = self.get_length_index()
        stdv_index = self.get_stdv_index()

        if event_start is -1 and event_end is -1:
            # get all the events of a given fast5 file
            print("index,signal,time,model,length,stdv")
            for i in range(0,self.get_event_count()):
                print(
                    i+1, # serial number
                    self.events[i][signal_index], # signal
                    self.events[i][time_index], # time
                    "".join( [ chr(item) for item in self.events[event_start][model_index] ]), # model
                    self.events[i][length_index], # length
                    self.events[i][stdv_index], # stdv
                    sep=",")

        elif event_end <= event_start:
            raise IOError("The start event should be less than end and there \
            should at least be one event")
        else:
            # get only events from start to end
            print("index,signal,time,model,length,stdv")
            for i in range(event_start,event_end):
                print(
                    i+1, # serial number
                    self.events[i][signal_index], # signal
                    self.events[i][time_index], # time
                    "".join( [ chr(item) for item in self.events[event_start][model_index] ]), # model
                    self.events[i][length_index], # length
                    self.events[i][stdv_index], # stdv
                    sep=",")


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

    def get_stdv_index(self):
        """ Returns an integer value representing the index of the stdv
            of the given fast5 file.
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        # The field header array containing names of each offest of pore model
        field_header_arr = self.events.dtype.names

        # Getting the index of stdv value
        stdv_index = -1
        for index,field in enumerate(field_header_arr):
            if field == "stdv":
                stdv_index = index
        return stdv_index

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


    def get_bp_from_events(self,event_start,event_end):
        """ Returns a list of characters representing base pairs of the range of
            events provided in the arguments.
        """
        self.assert_events() # Throw an error if the event data isn't populated.

        bp = [] # empty list that will contain chracters representing basepairs.

        model_index = self.get_model_state_index()

        # initially write every nucleutide in the kmer for the first event.
        initial_kmer = "".join( [ chr(item) for item in self.events[event_start][model_index] ] )
        for n in initial_kmer:
            bp.append(n)

        last_model_state = self.events[event_start][model_index] # represents the visited model_state

        for i in range(event_start+1,event_end):
            current_model_state = self.events[i][model_index] # represents the current model_state we are looking at
            if current_model_state != last_model_state: # basecall has happened

                # add the last digit of the kmer to the bp
                kmer = "".join( [ chr(item) for item in self.events[i][model_index] ] )
                bp.append(kmer[-1:])
            else:
               continue

            # Update the last model_state
            last_model_state = self.events[i][model_index]
        return bp

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
            if field == "mean":
                mean_signal = index
        return mean_signal

    def get_qname(self):
        self.assert_events()

        qname_path = '/Analyses/Basecall_1D_000/BaseCalled_template/Fastq'
        dset = self.handle[qname_path]
        return dset.value.decode("utf-8").split('\n')[0][1:]


    def get_list_event_data(self,event_start = -1, event_end = -1):

        signal_index = self.get_mean_signal_index()
        time_index = self.get_start_time_index()
        model_index = self.get_model_state_index()
        length_index = self.get_length_index()
        stdv_index = self.get_stdv_index()
        move = self.get_move_index()

        max_sig = 0
        min_sig = 100

        record = []
        record.append(self.get_qname())
        # record = "[\"" + str(self.get_qname()) + "\": "

        if event_start is -1 and event_end is -1:
            prev_move = -1
            # get all the events of a given fast5 file
            #print("index,signal,time,model,length,stdv")
            for i in range(0,self.get_event_count()):
                # if(i == (self.get_event_count()-1)):
                #     record = record.append(sub1)
                # else:
                if self.events[i][signal_index] > max_sig:
                    max_sig = self.events[i][signal_index]
                if self.events[i][signal_index] < min_sig:
                    min_sig = self.events[i][signal_index]
                if prev_move == -1:
                    if self.events[i][move] == 1:
                        prev_move = 0
                    # record.append(str("%06d" % prev_move))
                    record.append(str(prev_move))
                    sub1 = []
                    sub1.append([str(i+1), str(self.events[i][signal_index]),
                        str(self.events[i][time_index]),
                        "".join( [ chr(item) for item in self.events[event_start][model_index] ]),
                        str(self.events[i][length_index]),
                        str(self.events[i][stdv_index])])
                elif prev_move != -1 and self.events[i][move] == 0:
                    sub1.append([str(i+1), str(self.events[i][signal_index]),
                        str(self.events[i][time_index]),
                        "".join( [ chr(item) for item in self.events[event_start][model_index] ]),
                        str(self.events[i][length_index]),
                        str(self.events[i][stdv_index])])
                elif prev_move != -1 and self.events[i][move] == 1:
                    prev_move += 1
                    record.append(sub1)
                    # record.append(str("%06d" % prev_move))
                    record.append(str(prev_move))
                    sub1 = []
                    sub1.append([str(i+1), str(self.events[i][signal_index]),
                        str(self.events[i][time_index]),
                        "".join( [ chr(item) for item in self.events[event_start][model_index] ]),
                        str(self.events[i][length_index]),
                        str(self.events[i][stdv_index])])
            max_min = []
            max_min.append(str(max_sig))
            max_min.append(str(min_sig))
            record.append(sub1)
            # record.append(max_min)
            return record, max_min

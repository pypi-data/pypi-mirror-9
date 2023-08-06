#!/usr/bin/env python3

"""
a module to allow easier handling of BUFR files and messages
by providing several helper classes.
"""

#  #[ documentation
#
# This module implements a more pythonic interface layer
# around pybufr_ecmwf and is intended to make use of the BUFR
# file format easier and more intuitive for people used to python
# rather than fortran.
#
# Note about the use of the "#  #[" and "#  #]" comments:
#   these are folding marks for my favorite editor, emacs, combined with its
#   folding mode
#   (see http://www.emacswiki.org/emacs/FoldingMode for more details)
# Please do not remove them.
#
# For details on the revision history, refer to the log-notes in
# the mercurial revisioning system hosted at google code.
#
# Written by: J. de Kloe, KNMI (www.knmi.nl), Initial version 04-Feb-2010    
#
# Copyright J. de Kloe
# This software is licensed under the terms of the LGPLv3 Licence
# which can be obtained from https://www.gnu.org/licenses/lgpl.html

#  #]
#  #[ imported modules
from __future__ import (absolute_import, division,
                        print_function) #, unicode_literals)
import sys # os
import numpy   # array functionality
from .raw_bufr_file import RawBUFRFile
from .bufr_interface_ecmwf import BUFRInterfaceECMWF
from .helpers import python3
from .custom_exceptions import NoMsgLoadedError, CannotExpandFlagsError
#  #]

class DataValue:
    #  #[
    """
    a base class for data values
    """
    def __init__(self):
        self.value = None
        # pass
    def set_value(self, value):
        """ a method to set a value """
        self.value = value
        # pass
    def get_value(self):
        """ a method to get a value """
        return self.value
        # pass
    
    #  ==>value or string-value
    #  ==>already filled or not?
    #  ==>pointer to the associated descriptor object
    #  #]

class BUFRMessage: # [moved here from pybufr_ecmwf.py]
    #  #[
    """
    a base class for BUFR messages
    """
    def __init__(self):
        self.store_something = None
        # pass
    def do_something(self):
        """ do something """
        self.store_something = 1.2345
        # pass
    def do_somethingelse(self):
        """ do something else """
        self.store_something = 5.4321
        # pass

    #  ==>properties-list = [sec0, sec1, sec2, sec3 data]
    #  ==>list-of-descriptor-objects = []
    #  ==>finish (set num subsets, num delayed replications)
    #  ==>2D-data-array of data objects (num subsets x expanded num descriptors)
    #
    # possible methods:
    # -add_descriptor
    # -expand_descriptorList
    # -encode
    # -decode
    # -print_sections_012
    # -get_descriptor_properties
    # -fill_one_real_value
    # -fill_one_string_value
    # -get_one_real_value
    # -get_one_string_value
    # -...
    #  #]

#class BUFRFile(RawBUFRFile):
    #  #[
#    """
#    a base class for BUFR files
#    """
#    pass
#    # bufr-file [can reuse much functionality from what I have now in the
#    #            RawBUFRFile class in pybufr_ecmwf.py]
#    #  ==>some meta data
#    #  ==>list-of-bufr-msgs = []
    #  #]

# this class implements combined reading and decoding
class BUFRReader:
    #  #[
    """
    a class that combines reading and decoding of a BUFR file
    to allow easier reading and usage of BUFR files
    """
    def __init__(self, input_bufr_file, warn_about_bufr_size=True,
                 expand_flags=False, verbose=False):
        #  #[
        # get an instance of the RawBUFRFile class
        self.rbf = RawBUFRFile(warn_about_bufr_size=warn_about_bufr_size)

        self.verbose = verbose
        
        # open the file for reading, count nr of BUFR messages in it
        # and store its content in memory, together with
        # an array of pointers to the start and end of each BUFR message
        self.rbf.open(input_bufr_file, 'rb')
    
        # extract the number of BUFR messages from the file
        self.num_msgs = self.rbf.get_num_bufr_msgs()

        # keep track of which bufr message has been loaded and
        # decoded from this file
        self.msg_loaded = -1
        self.bufr_obj = None

        # allow manual choice of tables
        self.table_b_to_use = None
        self.table_c_to_use = None
        self.table_d_to_use = None
        self.tables_dir = None

        # expand flags to text
        self.expand_flags = expand_flags
        
        #  #]
    def setup_tables(self,table_b_to_use=None, table_c_to_use=None,
                     table_d_to_use=None, tables_dir=None):
        #  #[
        """
        allow manual choice of bufr tables
        """
        self.table_b_to_use = table_b_to_use
        self.table_c_to_use = table_c_to_use
        self.table_d_to_use = table_d_to_use
        self.tables_dir = tables_dir
        #  #]
    def get_next_msg(self):
        #  #[
        """
        step to the next BUFR message in the open file
        """
        (raw_msg, section_sizes, section_start_locations) = \
                 self.rbf.get_next_raw_bufr_msg()
        # print('(raw_msg, section_sizes, section_start_locations) = ',\
        #       (raw_msg, section_sizes, section_start_locations))
        self.bufr_obj = BUFRInterfaceECMWF(raw_msg,
                                           section_sizes,
                                           section_start_locations,
                                           expand_flags=self.expand_flags,
                                           verbose=self.verbose)
        self.bufr_obj.decode_sections_012()
        self.bufr_obj.setup_tables(self.table_b_to_use, self.table_c_to_use,
                                   self.table_d_to_use, self.tables_dir)
        self.bufr_obj.decode_data()

        #nsub = int(self.bufr_obj.get_num_subsets())
        #n = len(self.bufr_obj.values)/nsub
        n = self.bufr_obj.actual_nr_of_expanded_descriptors
        #self.bufr_obj.fill_descriptor_list(nr_of_expanded_descriptors=n)

        self.bufr_obj.decode_sections_0123()
        self.bufr_obj.fill_descriptor_list_subset(subset=1)
        
        self.msg_loaded = self.rbf.last_used_msg
        #  #]
    def get_num_subsets(self):
        #  #[
        """
        request the number of subsets in the current BUFR message
        """
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError
        return self.bufr_obj.get_num_subsets()
        #  #]
    def get_num_elements(self):
        #  #[
        """
        request the number of elements (descriptors) in the current subset
        """
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        return self.bufr_obj.get_num_elements()
        #  #]
    def get_value(self, descr_nr, subset_nr, get_cval=False):
        #  #[
        """
        request a value for a given subset and descriptor number
        """
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        val = self.bufr_obj.get_value(descr_nr, subset_nr, get_cval)
        return val
        #  #]
    def get_values(self, descr_nr, get_cval=False):

        #  #[
        """
        request an array of values containing the values
        for a given descriptor number for all subsets
        """
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        self.bufr_obj.delayed_repl_check_for_incorrect_use()

        vals = self.bufr_obj.get_values(descr_nr, get_cval)

        return vals
        #  #]
    def get_subset_values(self, subset_nr , get_cval=False):
         #  #[
        """
        request an array of values containing the values
        for a given subset for this bufr message
        """
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        vals = self.bufr_obj.get_subset_values(subset_nr, get_cval)

        return vals
        #  #]
    def get_values_as_2d_array(self):
        #  #[
        """
        a convenience method to allow retrieving all data in
        a bufr message in the form of a 2D array. This first index
        runs over the subsets, the second over the descriptors.
        """
        if (self.msg_loaded == -1):
            txt = 'Sorry, no BUFR messages available'
            raise NoMsgLoadedError(txt)

        if self.expand_flags:
            errtxt = ('ERROR: get_values_as_2d_array only returns numeric '+
                      'results and cannot be used together with the '+
                      'expand_flags option.'+
                      'You will need to extract one element of one row of '+
                      'elements at a time in this case.')
            raise CannotExpandFlagsError(errtxt)
            
        self.bufr_obj.delayed_repl_check_for_incorrect_use()

        num_subsets  = self.bufr_obj.get_num_subsets()
        num_elements = self.bufr_obj.get_num_elements()
        result = numpy.zeros([num_subsets, num_elements], dtype=float)

        #print('DEBUG: num_subsets = ', num_subsets)
        #print('DEBUG: num_elements = ', num_elements)

        for descr_nr in range(num_elements):
            
            result[:, descr_nr] = self.bufr_obj.get_values(descr_nr)

        return result
        #  #]
    def get_names_and_units(self, subset=1):
        #  #[ request name and unit of each descriptor for the given subset
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError
        
        (list_of_names, list_of_units) = \
                        self.bufr_obj.get_names_and_units(subset)

        return (list_of_names, list_of_units)
        #  #]
    def get_names(self, subset=1):
        #  #[ request name of each descriptor for the given subset
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        (list_of_names, list_of_units) = \
                        self.bufr_obj.get_names_and_units(subset)
        return list_of_names
        #  #]
    def get_units(self, subset=1):
        #  #[ request unit of each descriptor for the given subset
        if (self.msg_loaded == -1):
            raise NoMsgLoadedError

        (list_of_names, list_of_units) = \
                        self.bufr_obj.get_names_and_units(subset)

        return list_of_units
        #  #]        
    def close(self):
        #  #[
        """
        close the file object
        """
        self.rbf.close()
        #  #]
    #  #]

if __name__ == "__main__":
    #  #[ test program
    print("Starting test program:")
    
    # this is how I think the BUFR module interfacing should look like
    
    # get a msg instance
    BMSG = BUFRMessage()
    # all sections should be filled with sensible defaults but ofcourse
    # the user should be able to change all of them
    # also the user should be able to insert a bufr table name to be
    # used, in contrast with the ECMWF method of using the metadata
    # to construct the BUFR table name. In that case the symbolic link
    # to the constructed BUFR table name should be rerouted to the name
    # provided by the user, to trick the ECMWF library in using it.
    
    # built the template
    #bm.add_descriptor()
    #bm.add_descriptor()
    #bm.add_descriptor()
    
    # expand any D-table entries
    #bm.expand_descriptor_list()
    
    #ns = 361
    #bm.set_num_subsets(ns)
    #for ss in range(ns):
    #    bm.set_fill_index_to_start_subset(ss)
    #    bm.fill_one_element(val, descr_code, descr_text)
    #    bm.fill_one_element(val, descr_code, descr_text)
    #    bm.fill_one_element(val, descr_code, descr_text)
    
    #bf = BUFRFile()
    #bf.open(file = '', mode = 'w')
    #bf.write(bm) # this should automatically do the encoding
    #bf.close()
    
    # further ideas:
    # -allow generation of a custom minimal BUFR table
    #  holding only the entries needed to decode/encode the
    #  current BUFR message
    # -add methods to compose a BUFR table from scratch
    #  and/or modify it (add, delete, save, load)
    #
    #  #]
    

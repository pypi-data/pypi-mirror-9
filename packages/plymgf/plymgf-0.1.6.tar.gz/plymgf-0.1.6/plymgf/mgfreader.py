#!/usr/bin/env python
# encoding: utf-8
"""mgfreader.py is a reader for mgf files 
@author: Vezin Aurelien
@license: CeCILL-B"""

import sys
sys.path.append('../')
from plymgf.classlexer import read_mgf


class MGFReader(object):
    """ This class is use to read an MGF File 
    @ivar data: the data from the parser
    @type data: dict(string: list(dict(string: any)) | 
    dict(string : any))
    @ivar ions: the ion we are looking
    @type ions: int """
    
    def __init__(self, mgf_path):
        """ init of the class """
        self._data = read_mgf(mgf_path)
        self._ions = 0
    
    def get_raw_data(self):
        """return the pure data 
        @return: return all the data parse with the parser
        @rtype: dict(string : any)"""
        return self._data
    
    def get_cle(self):
        """return the enzyme use to make the disgestion
        @return: the enzyme to make the disgestion (Trypsin for
        example)
        @rtype: string"""
        return self._data["meta"]["cle"]
    
    def get_accession(self):
        """return the database entries to be search
        @return: the database entries to be search
        @rtype: string"""
        return self._data["meta"]["accession"]
    
    def get_itol(self):
        """return the error tolerance (depend of itolu)
        @return: the error tolerance
        @rtype: float/int"""
        return self._data["meta"]["itol"]
    
    def get_itolu(self):
        """return the error tolerance unit
        @return: the error tolerance unit (example PPM)
        @rtype: string"""
        return self._data["meta"]["itolu"]
    
    def get_mass(self):
        """return the type of the mass Monoisotopic/Average
        @return: the type of mass (Monoisotopic/Average)
        @rtype: string"""
        return self._data["meta"]["mass"]
        
    def get_precursor(self):
        """return the precursor mass
        @return: a precurosor mass m/z >100
        @rtype: float"""
        return self._data["meta"]["precursor"]
        
    def get_seg(self):
        """return the protein mass in KDa
        @return: a protein mass in KDa
        @rtype: int/float"""
        return self._data["meta"]["seg"]
    
    def get_taxonomy(self):
        """return the taxonomy"""
        return self._data["meta"]["taxonomy"]
    
    def get_usermail(self):
        """return the mail of the user
        @return: the mail of the user
        @rtype: string"""
        return self._data["meta"]["usermail"]
    
    def get_charge(self):
        """return the meta charges
        @return: the possibles charges of the protein
        @rtype: list(int)"""
        return self._data["meta"]["charges"]
    
    def next_ion(self):
        """go to the next ion"""
        if len(self._data["ions"]) > self._ions + 1:
            self._ions = self._ions + 1
            return 0
        else:
            return 1
    
    def get_ion_charge(self):
        """return the charge of the ion
        @return: the charges possibles for the ion
        @rtype: list(int)"""
        return self._data["ions"][self._ions]["charges"]
    
    def get_ion_pepmass(self):
        """return the mass and the intensity of the peptide
        @return: a tuple with the mass and the intensity of the mass
        on the ms spectrum
        @rtype: (float, float/int)"""
        return self._data["ions"][self._ions]["pepmass"]
    
    def get_ion_rtinseconds(self):
        """return the time when the ion was analyse
        @return: the time when the ms/ms analyse have been done
        @rtype: int/float"""
        return self._data["ions"][self._ions]["rtinseconds"]
    
    def get_ion_seq(self):
        """return the sequence of the ion
        @return: the sequence of the ion
        @rtype: string"""
        return self._data["ions"][self._ions]["seq"]

    def get_ion_title(self):
        """return the title of the ion
        @return: the title of the ion
        @rtype: string"""
        return self._data["ions"][self._ions]["title"]
    
    def get_ion_tol(self):
        """return the error tolerance (depend of tolu) of the ion
        @return: the error tolerance value of the ion
        @rtype: int/float"""
        return self._data["ions"][self._ions]["tol"]
    
    def get_ion_tolu(self):
        """return the error tolerance unit of the ion
        @return: the error tolerance unit of the ion
        @rtype: string"""
        return self._data["ions"][self._ions]["tolu"]
    
    def get_ion_peaks(self):
        """return the list of peak of the ion
        @return: a list of peak of the ions with the m/z 
        the intensity and the charge of each peak
        @rtype: list(int/float, int/float, int)"""
        return self._data["ions"][self._ions]["peaklist"]

if __name__ == "__main__":
    TEST = MGFReader(sys.argv[1])
    TEST.next_ion()
    TEST.next_ion()
    print TEST.get_ion_peaks()
    

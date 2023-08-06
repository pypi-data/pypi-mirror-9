A MGF parser
=======================

/!\Installation with pip corrected since 1.7 version

This project allow you to read MGF files.

If you find a bug, have a problem to parse a MGF file or
have a feature request please send it to me at : aurelien.vezin at etu.unistra.fr 

it's use like :

    from plymgf.mgfreader import MGFReader 
    
    res = MGFReader('path_to_your_file.mgf')

To have the same behaviour than in previous versions do

    data = res.get_raw_data()

You can get some metadata with the methods:
 - get_cle 
 - get_accession
 - get_itol
 - get_itolu
 - get_mass
 - get_precursor
 - get_seg
 - get_taxonomy
 - get_usermail
 - get_charge

By default you are on the first ions;
To go on the next one use the method "next_ion".
If you are on the last ions the method will also return 1.

You can get some ions data with the methods:
 - get_ion_charge
 - get_ion_pepmass
 - get_ion_rtinseconds
 - get_ion_seq
 - get_ion_title
 - get_ion_tol
 - get_ion_tolu
 - get_ion_peaks

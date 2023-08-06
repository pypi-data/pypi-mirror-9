#!/usr/bin/env python
from __future__ import print_function
"""

    test_combinatorics.py

        test product, combine, permute, combine_with_replacement

"""


workdir = 'tmp_test_combinatorics'
#sub-1s resolution in system?
one_second_per_job = None

import os
import sys

# add grandparent to search path for testing
grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, grandparent_dir)

# module name = script name without extension
module_name = os.path.splitext(os.path.basename(__file__))[0]


# funky code to import by file name
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ruffus_name = os.path.basename(parent_dir)
ruffus = __import__ (ruffus_name)
try:
    attrlist = ruffus.combinatorics.__all__
except AttributeError:
    attrlist = dir (ruffus.combinatorics)
for attr in attrlist:
    if attr[0:2] != "__":
        globals()[attr] = getattr (ruffus.combinatorics, attr)

for attr in "pipeline_run", "pipeline_printout", "suffix", "transform", "split", "merge", "dbdict", "follows", "Pipeline", "formatter", "output_from":
    globals()[attr] = getattr (ruffus, attr)
RethrownJobError = ruffus.ruffus_exceptions.RethrownJobError
RUFFUS_HISTORY_FILE      = ruffus.ruffus_utility.RUFFUS_HISTORY_FILE
CHECKSUM_FILE_TIMESTAMPS = ruffus.ruffus_utility.CHECKSUM_FILE_TIMESTAMPS


import unittest
import shutil
try:
    from StringIO import StringIO
except:
    from io import StringIO
import re



def touch (outfile):
    with open(outfile, "w"):
        pass


#___________________________________________________________________________
#
#   generate_initial_files1
#___________________________________________________________________________
def generate_initial_files1(outfile):
    touch(outfile)

#___________________________________________________________________________
#
#   generate_initial_files2
#___________________________________________________________________________
def generate_initial_files2(outfile):
    touch(outfile)

#___________________________________________________________________________
#
#   generate_initial_files3
#___________________________________________________________________________
def generate_initial_files3(outfile):
    touch(outfile)

#___________________________________________________________________________
#
#   test_product_task
#___________________________________________________________________________
def test_product_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    with open(outfile, "w") as p:
        p.write(prefices + ",")


#___________________________________________________________________________
#
#   test_product_merged_task
#___________________________________________________________________________
def test_product_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())

#___________________________________________________________________________
#
#   test_product_misspelt_capture_error_task
#___________________________________________________________________________
def test_product_misspelt_capture_error_task( infiles, outfile):
    """
    FILE_PART mispelt as FILE_PART
    """
    touch(outfile)


#___________________________________________________________________________
#
#   test_product_out_of_range_formatter_ref_error_task
#___________________________________________________________________________
def test_product_out_of_range_formatter_ref_error_task( infiles, outfile, ignored_filter):
    """
    {path[2][0]} when len(path) == 1
    """
    touch(outfile)

#___________________________________________________________________________
#
#   test_product_formatter_ref_index_error_task
#___________________________________________________________________________
def test_product_formatter_ref_index_error_task( infiles, outfile, ignored_filter):
    """
    {path[0][0][1000} when len of the path string len(path[0][0]) < 1000
    """
    touch(outfile)

#___________________________________________________________________________
#
#   test_combinations2_task
#___________________________________________________________________________
def test_combinations2_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test combinations with k-tuple = 2
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")


def test_combinations2_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())

#___________________________________________________________________________
#
#   test_combinations3_task
#___________________________________________________________________________
def test_combinations3_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test combinations with k-tuple = 3
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")

def test_combinations3_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())


#___________________________________________________________________________
#
#   test_permutations2_task
#___________________________________________________________________________
def test_permutations2_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test permutations with k-tuple = 2
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")

def test_permutations2_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())


#___________________________________________________________________________
#
#   test_permutations3_task
#___________________________________________________________________________
def test_permutations3_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test permutations with k-tuple = 3
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")

def test_permutations3_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())



#___________________________________________________________________________
#
#   test_combinations_with_replacement2_task
#___________________________________________________________________________
def test_combinations_with_replacement2_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test combinations_with_replacement with k-tuple = 2
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")

def test_combinations_with_replacement2_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())


#___________________________________________________________________________
#
#   test_combinations_with_replacement3_task
#___________________________________________________________________________
def test_combinations_with_replacement3_task( infiles, outfile,
            prefices,
            subpath,
            subdir):
    """
        Test combinations_with_replacement with k-tuple = 3
    """
    with open(outfile, "w") as outf:
        outf.write(prefices + ",")

def test_combinations_with_replacement3_merged_task( infiles, outfile):
    with open(outfile, "w") as p:
        for infile in sorted(infiles):
            with open(infile) as ii:
                p.write(ii.read())



def cleanup_tmpdir():
    os.system('rm -f %s %s' % (os.path.join(workdir, '*'), RUFFUS_HISTORY_FILE))


test_pipeline1 = Pipeline("test1")
test_pipeline2 = Pipeline("test2")
gen_task1 = test_pipeline1.originate(task_func  = generate_initial_files1,
                                     name       = "WOWWWEEE",
                                     output     = [workdir +  "/" + prefix + "_name.tmp1" for prefix in "abcd"])
test_pipeline1.originate(            task_func  = generate_initial_files2,
                                     output     = [workdir +  "/e_name.tmp1", workdir +  "/f_name.tmp1"])
test_pipeline1.originate(            task_func  = generate_initial_files3,
                                     output     = [workdir +  "/g_name.tmp1", workdir +  "/h_name.tmp1"])
test_pipeline1.product(              task_func  = test_product_task,
                                     input      = [workdir +  "/" + prefix + "_name.tmp1" for prefix in "abcd"],
                                     filter     = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                     input2     = generate_initial_files2,
                                     filter2    = formatter(),
                                     input3     = generate_initial_files3,
                                     filter3    = formatter(r"tmp1$" ),
                                     output     = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.{basename[2][0]}.tmp2",
                                     extras     = [ "{basename[0][0][0]}{basename[1][0][0]}{basename[2][0][0]}",       # extra: prefices only (abcd etc)
                                                    "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                                    "{subdir[0][0][0]}"]).follows("WOWWWEEE").follows(gen_task1).follows(generate_initial_files1).follows("generate_initial_files1")
test_pipeline1.merge(               task_func   = test_product_merged_task,
                                    input       = test_product_task,
                                    output      = workdir +  "/merged.results")
test_pipeline1.product(             task_func   = test_product_misspelt_capture_error_task,
                                    input       = gen_task1,
                                    filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                    output      = "{path[0][0]}/{FILEPART[0][0]}.tmp2")
test_pipeline1.product(             task_func   = test_product_out_of_range_formatter_ref_error_task,
                                    input       = generate_initial_files1,  #
                                    filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                    output      = "{path[2][0]}/{basename[0][0]}.tmp2",
                                    extras      = ["{FILE_PART[0][0]}"])
test_pipeline1.product(             task_func   = test_product_formatter_ref_index_error_task,
                                    input       = output_from("generate_initial_files1"),
                                    filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                    output      = "{path[0][0][1000]}/{basename[0][0]}.tmp2",
                                    extras      = ["{FILE_PART[0][0]}"])
test_pipeline1.combinations(task_func   = test_combinations2_task,
                            input       = generate_initial_files1,      # gen_task1
                            filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                            tuple_size  = 2,
                            output      = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.tmp2",
                            extras      = ["{basename[0][0][0]}{basename[1][0][0]}",       # extra: prefices
                                           "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                           "{subdir[0][0][0]}"])
test_pipeline1.merge(task_func  = test_combinations2_merged_task,
                     input      = test_combinations2_task,
                     output     = workdir +  "/merged.results")
test_pipeline1.combinations(    task_func   = test_combinations3_task,
                                input       = output_from("WOWWWEEE"),
                                filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                tuple_size  = 3,
                                output      = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.{basename[2][0]}.tmp2",
                                extras      = ["{basename[0][0][0]}{basename[1][0][0]}{basename[2][0][0]}",       # extra: prefices
                                               "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                               "{subdir[0][0][0]}"])

test_pipeline1.merge(test_combinations3_merged_task, test_combinations3_task, workdir +  "/merged.results")
test_pipeline1.permutations(task_func   = test_permutations2_task,
                            input       = output_from("WOWWWEEE"),
                            filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                            tuple_size  = 2,
                            output      = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.tmp2",
                            extras      = ["{basename[0][0][0]}{basename[1][0][0]}",       # extra: prefices
                                          "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                          "{subdir[0][0][0]}"])

test_pipeline2.merge(test_permutations2_merged_task, test_permutations2_task, workdir +  "/merged.results")



test_pipeline2.permutations(task_func   = test_permutations3_task,
                            input       = output_from("WOWWWEEE"),
                            filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                            tuple_size  = 3,
                            output      = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.{basename[2][0]}.tmp2",
                            extras      = ["{basename[0][0][0]}{basename[1][0][0]}{basename[2][0][0]}",       # extra: prefices
                                          "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                          "{subdir[0][0][0]}"])
test_pipeline2.merge(test_permutations3_merged_task, test_permutations3_task, workdir +  "/merged.results")
test_pipeline2.combinations_with_replacement(test_combinations_with_replacement2_task,
                                            input = output_from("WOWWWEEE"),
                                            filter = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                            tuple_size = 2,
                                            output = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.tmp2",
                                            extras = ["{basename[0][0][0]}{basename[1][0][0]}",       # extra: prefices
                                            "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                            "{subdir[0][0][0]}"])
test_pipeline2.merge(test_combinations_with_replacement2_merged_task,
    test_combinations_with_replacement2_task, workdir +  "/merged.results")
test_pipeline2.combinations_with_replacement(   task_func   = test_combinations_with_replacement3_task,
                                                input       = output_from("WOWWWEEE"),
                                                filter      = formatter(".*/(?P<FILE_PART>.+).tmp1$" ),
                                                tuple_size  = 3,
                                                output      = "{path[0][0]}/{FILE_PART[0][0]}.{basename[1][0]}.{basename[2][0]}.tmp2",
                                                extras      = ["{basename[0][0][0]}{basename[1][0][0]}{basename[2][0][0]}",       # extra: prefices
                                                              "{subpath[0][0][0]}",      # extra: path for 2nd input, 1st file
                                                              "{subdir[0][0][0]}"])
test_pipeline2.merge(test_combinations_with_replacement3_merged_task,
    test_combinations_with_replacement3_task, workdir +  "/merged.results")


class TestCombinatorics(unittest.TestCase):
    def setUp(self):
        try:
            os.mkdir(workdir)
        except OSError:
            pass

    #___________________________________________________________________________
    #
    #   test product() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_product_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()
        s = StringIO()
        test_pipeline2.printout(s, [test_product_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('Job needs update:.*Missing files.*'
                      '\[.*tmp_test_combinatorics/a_name.tmp1, '
                      '.*tmp_test_combinatorics/e_name.tmp1, '
                      '.*tmp_test_combinatorics/h_name.tmp1, '
                      '.*tmp_test_combinatorics/a_name.e_name.h_name.tmp2\]', s.getvalue(), re.DOTALL))

    def test_product_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_product_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         "aeg,aeh,afg,afh,beg,beh,bfg,bfh,ceg,ceh,cfg,cfh,deg,deh,dfg,dfh,")

    #___________________________________________________________________________
    #
    #   test product() pipeline_printout diagnostic error messsages
    #
    #       require verbose >= 3 or an empty jobs list
    #___________________________________________________________________________
    def test_product_misspelt_capture_error(self):
        """Misspelt named capture group
            Requires verbose >= 3 or an empty jobs list
        """
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_product_misspelt_capture_error_task], verbose=3, wrap_width = 10000)
        self.assertIn("Warning: File match failure: Unmatched field 'FILEPART'", s.getvalue())


    def test_product_out_of_range_formatter_ref_error(self):
        """
        {path[2][0]} when len(path) == 1
            Requires verbose >= 3 or an empty jobs list
        """
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_product_out_of_range_formatter_ref_error_task], verbose=3, wrap_width = 10000)
        self.assertIn("Warning: File match failure: Unmatched field 2", s.getvalue())

    def test_product_formatter_ref_index_error(self):
        """
        {path[0][0][1000} when len of the path string len(path[0][0]) < 1000
            Requires verbose >= 3 or an empty jobs list
        """
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_product_formatter_ref_index_error_task], verbose=3, wrap_width = 10000)
        self.assertIn("Warning: File match failure: Unmatched field string index out of range", s.getvalue())
        #print s.getvalue()


    #___________________________________________________________________________
    #
    #   test combinations() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_combinations2_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline1.printout(s, [test_combinations2_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('Job needs update:.*Missing files.*'
                      '\[.*tmp_test_combinatorics/a_name.tmp1, '
                        '.*tmp_test_combinatorics/b_name.tmp1, '
                        '.*tmp_test_combinatorics/a_name.b_name.tmp2\]', s.getvalue(), re.DOTALL))


    def test_combinations2_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_combinations2_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                              'ab,ac,ad,bc,bd,cd,')

    #___________________________________________________________________________
    #
    #   test combinations() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_combinations3_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_combinations3_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search(
                       '\[.*tmp_test_combinatorics/a_name.tmp1, '
                       '.*tmp_test_combinatorics/b_name.tmp1, '
                       '.*tmp_test_combinatorics/c_name.tmp1, '
                       '.*tmp_test_combinatorics/a_name.b_name.c_name.tmp2\]', s.getvalue()))

    def test_combinations3_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_combinations3_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         "abc,abd,acd,bcd,")


    #___________________________________________________________________________
    #
    #   test permutations() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_permutations2_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_permutations2_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('\[.*tmp_test_combinatorics/a_name.tmp1, '
                      '.*tmp_test_combinatorics/b_name.tmp1, '
                      '.*tmp_test_combinatorics/a_name.b_name.tmp2\]', s.getvalue()))

    def test_permutations2_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_permutations2_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         "ab,ac,ad,ba,bc,bd,ca,cb,cd,da,db,dc,")

    #___________________________________________________________________________
    #
    #   test permutations() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_permutations3_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_permutations3_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('\[.*tmp_test_combinatorics/a_name.tmp1, '
                       '.*tmp_test_combinatorics/b_name.tmp1, '
                       '.*tmp_test_combinatorics/c_name.tmp1, '
                       '.*tmp_test_combinatorics/a_name.b_name.c_name.tmp2\]', s.getvalue()))

    def test_permutations3_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_permutations3_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         'abc,abd,acb,acd,adb,adc,bac,bad,bca,bcd,bda,bdc,cab,cad,cba,cbd,cda,cdb,dab,dac,dba,dbc,dca,dcb,')


    #___________________________________________________________________________
    #
    #   test combinations_with_replacement() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_combinations_with_replacement2_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_combinations_with_replacement2_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('\[.*tmp_test_combinatorics/a_name.tmp1, '
                      '.*tmp_test_combinatorics/b_name.tmp1, '
                      '.*tmp_test_combinatorics/a_name.b_name.tmp2\]', s.getvalue()))

    def test_combinations_with_replacement2_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_combinations_with_replacement2_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         "aa,ab,ac,ad,bb,bc,bd,cc,cd,dd,")

    #___________________________________________________________________________
    #
    #   test combinations_with_replacement() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_combinations_with_replacement3_printout(self):
        """Input file exists, output doesn't exist"""
        cleanup_tmpdir()

        s = StringIO()
        test_pipeline2.printout(s, [test_combinations_with_replacement3_merged_task], verbose=5, wrap_width = 10000)
        self.assertTrue(re.search('\[.*tmp_test_combinatorics/a_name.tmp1, '
                       '.*tmp_test_combinatorics/b_name.tmp1, '
                       '.*tmp_test_combinatorics/c_name.tmp1, '
                       '.*tmp_test_combinatorics/a_name.b_name.c_name.tmp2\]', s.getvalue()))

    def test_combinations_with_replacement3_run(self):
        """Run product"""
        # output is up to date, but function body changed (e.g., source different)
        cleanup_tmpdir()
        test_pipeline2.run([test_combinations_with_replacement3_merged_task], verbose=0, multiprocess = 100, one_second_per_job = one_second_per_job)
        with open(workdir +  "/merged.results") as oo:
            self.assertEqual(oo.read(),
                         'aaa,aab,aac,aad,abb,abc,abd,acc,acd,add,bbb,bbc,bbd,bcc,bcd,bdd,ccc,ccd,cdd,ddd,')


    #___________________________________________________________________________
    #
    #   cleanup
    #___________________________________________________________________________
    def tearDown(self):
        shutil.rmtree(workdir)



#
#   Necessary to protect the "entry point" of the program under windows.
#       see: http://docs.python.org/library/multiprocessing.html#multiprocessing-programming
#
if __name__ == '__main__':
    #pipeline_printout(sys.stdout, [test_product_task], verbose = 5)
    unittest.main()

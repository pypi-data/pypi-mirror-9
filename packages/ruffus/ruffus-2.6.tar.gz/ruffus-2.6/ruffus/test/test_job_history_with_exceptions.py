#!/usr/bin/env python
from __future__ import print_function
"""

    test_job_history_with_exceptions.py

        Make sure that when an exception is thrown only the current and following tasks fail

"""

workdir = 'tmp_test_job_history_with_exceptions'
#sub-1s resolution in system?
one_second_per_job = None
throw_exception = False

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
for attr in "pipeline_run", "pipeline_printout", "suffix", "transform", "split", "merge", "dbdict", "follows", "originate", "collate", "formatter", "Pipeline":
    globals()[attr] = getattr (ruffus, attr)
RethrownJobError =  ruffus.ruffus_exceptions.RethrownJobError
RUFFUS_HISTORY_FILE           = ruffus.ruffus_utility.RUFFUS_HISTORY_FILE
CHECKSUM_FILE_TIMESTAMPS      = ruffus.ruffus_utility.CHECKSUM_FILE_TIMESTAMPS
get_default_history_file_name = ruffus.ruffus_utility.get_default_history_file_name






#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888
#
#   imports
#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

import unittest
import shutil
try:
    from StringIO import StringIO
except:
    from io import StringIO
import re


#___________________________________________________________________________
#
#   generate_initial_files1
#___________________________________________________________________________
@originate([workdir +  "/" + prefix + "_name.tmp1" for prefix in "abcd"])
def generate_initial_files1(on):
    with open(on, 'w') as outfile:
        pass

#___________________________________________________________________________
#
#   generate_initial_files2
#___________________________________________________________________________
@originate([workdir +  "/e_name.tmp1", workdir +  "/f_name.tmp1"])
def generate_initial_files2(on):
    with open(on, 'w') as outfile:
        pass

#___________________________________________________________________________
#
#   generate_initial_files3
#___________________________________________________________________________
@originate([workdir +  "/g_name.tmp1", workdir +  "/h_name.tmp1"])
def generate_initial_files3(on):
    with open(on, 'w') as outfile:
        pass

#___________________________________________________________________________
#
#   generate_initial_files1
#___________________________________________________________________________
@originate(workdir +  "/i_name.tmp1")
def generate_initial_files4(on):
    with open(on, 'w') as outfile:
        pass

#___________________________________________________________________________
#
#   test_task2
#___________________________________________________________________________
@collate([generate_initial_files1, generate_initial_files2, generate_initial_files3,
            generate_initial_files4],
         formatter(),
         "{path[0]}/all.tmp2")
#@transform([generate_initial_files1, generate_initial_files2, generate_initial_files3,
#            generate_initial_files4],
#            formatter( ),
#            "{path[0]}/{basename[0]}.tmp2")
def test_task2( infiles, outfile):
    with open(outfile, "w") as p:
        pass
    #print >>sys.stderr, "8" * 80, "\n", "    task2 :%s %s " % (infiles, outfile)

#___________________________________________________________________________
#
#   test_task3
#___________________________________________________________________________
@transform(test_task2, suffix(".tmp2"), ".tmp3")
def test_task3( infile, outfile):
    global throw_exception
    if throw_exception != None:
        throw_exception = not throw_exception
    if throw_exception:
        #print >>sys.stderr, "Throw exception for ", infile, outfile
        raise Exception("oops")
    else:
        #print >>sys.stderr, "No throw exception for ", infile, outfile
        pass
    with open(outfile, "w") as p: pass
    #print >>sys.stderr, "8" * 80, "\n", "    task3 :%s %s " % (infile, outfile)

#___________________________________________________________________________
#
#   test_task4
#___________________________________________________________________________
@transform(test_task3, suffix(".tmp3"), ".tmp4")
def test_task4( infile, outfile):
    with open(outfile, "w") as p: pass
    #print >>sys.stderr, "8" * 80, "\n", "    task4 :%s %s " % (infile, outfile)




def cleanup_tmpdir():
    os.system('rm -f %s %s' % (os.path.join(workdir, '*'), RUFFUS_HISTORY_FILE))


VERBOSITY = 5
VERBOSITY = 11

cnt_pipelines = 0
class Test_job_history_with_exceptions(unittest.TestCase):
    def setUp(self):
        try:
            os.mkdir(workdir)
        except OSError:
            pass

    #___________________________________________________________________________
    #
    #   test product() pipeline_printout and pipeline_run
    #___________________________________________________________________________
    def test_job_history_with_exceptions(self):
        cleanup_tmpdir()
        s = StringIO()
        pipeline_printout(s, [test_task4], verbose=VERBOSITY, wrap_width = 10000)
        #print s.getvalue()


    def create_pipeline (self):
        #each pipeline has a different name
        global cnt_pipelines
        cnt_pipelines = cnt_pipelines + 1
        test_pipeline = Pipeline("test %d" % cnt_pipelines)

        test_pipeline.originate(task_func   = generate_initial_files1,
                                output      = [workdir +  "/" + prefix + "_name.tmp1" for prefix in "abcd"])

        test_pipeline.originate(task_func   = generate_initial_files2,
                                output      = [workdir +  "/e_name.tmp1", workdir +  "/f_name.tmp1"])

        test_pipeline.originate(task_func   = generate_initial_files3,
                                output      = [workdir +  "/g_name.tmp1", workdir +  "/h_name.tmp1"])

        test_pipeline.originate(task_func   = generate_initial_files4,
                                output      = workdir +  "/i_name.tmp1")

        test_pipeline.collate(  task_func   = test_task2,
                                input       = [generate_initial_files1,
                                               generate_initial_files2,
                                               generate_initial_files3,
                                               generate_initial_files4],
                                filter      = formatter(),
                                output      = "{path[0]}/all.tmp2")

        test_pipeline.transform(task_func   = test_task3,
                                input       = test_task2,
                                filter      = suffix(".tmp2"),
                                output      = ".tmp3")

        test_pipeline.transform(task_func   = test_task4,
                                input       = test_task3,
                                filter      = suffix(".tmp3"),
                                output      = ".tmp4")
        return test_pipeline


    def test_job_history_with_exceptions_run(self):
        """Run"""
        for i in range(1):
            cleanup_tmpdir()
            try:
                pipeline_run([test_task4], verbose = 0,
                             #multithread = 2,
                             one_second_per_job = one_second_per_job)
            except:
                pass
            s = StringIO()
            pipeline_printout(s, [test_task4], verbose=VERBOSITY, wrap_width = 10000)
            #
            # task 2 should be up to date because exception was throw in task 3
            #
            pipeline_printout_str = s.getvalue()
            correct_order = not re.search('Tasks which will be run:.*\n(.*\n)*Task = test_task2', pipeline_printout_str)
            if not correct_order:
                print(pipeline_printout_str)
            self.assertTrue(correct_order)
            sys.stderr.write(".")
        print()



    def test_newstyle_recreate_job_history(self):
        """Run"""
        test_pipeline = self.create_pipeline()
        global throw_exception
        throw_exception = None
        cleanup_tmpdir()

        #
        #      print "Initial run without creating sqlite file"
        #
        test_pipeline.run([test_task4], verbose = 0,
                     checksum_level = CHECKSUM_FILE_TIMESTAMPS,
                     multithread = 10,
                     one_second_per_job = one_second_per_job)

        #
        #   print "printout without sqlite"
        #
        s = StringIO()
        test_pipeline.printout(s, [test_task4], checksum_level = CHECKSUM_FILE_TIMESTAMPS)
        self.assertTrue(not re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue()))
        #
        # print "printout expecting sqlite file"
        #
        s = StringIO()
        test_pipeline.printout(s, [test_task4])
        self.assertTrue(re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue()))
        #
        #   print "Regenerate sqlite file"
        #
        test_pipeline.run([test_task4],
                     checksum_level = CHECKSUM_FILE_TIMESTAMPS,
                     history_file = get_default_history_file_name (),
                     multithread = 1,
                     verbose = 0,
                     touch_files_only = 2,
                     one_second_per_job = one_second_per_job)
        #
        # print "printout expecting sqlite file"
        #
        s = StringIO()
        test_pipeline.printout(s, [test_task4], verbose = VERBOSITY)
        succeed = not re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue())
        if not succeed:
            print(s.getvalue(), file=sys.stderr)
        self.assertTrue(succeed)

        throw_exception = False

    #
    def test_newstyle_job_history_with_exceptions_run(self):
        """Run"""
        test_pipeline = self.create_pipeline()
        for i in range(1):
            cleanup_tmpdir()
            try:
                test_pipeline.run([test_task4], verbose = 0,
                             #multithread = 2,
                             one_second_per_job = one_second_per_job)
            except:
                pass
            s = StringIO()
            test_pipeline.printout(s, [test_task4], verbose=VERBOSITY, wrap_width = 10000)
            #
            # task 2 should be up to date because exception was throw in task 3
            #
            pipeline_printout_str = s.getvalue()
            correct_order = not re.search('Tasks which will be run:.*\n(.*\n)*Task = test_task2', pipeline_printout_str)
            if not correct_order:
                print(pipeline_printout_str)
            self.assertTrue(correct_order)
            sys.stderr.write(".")
        print()



    def test_recreate_job_history(self):
        """Run"""
        global throw_exception
        throw_exception = None
        cleanup_tmpdir()

        #
        #      print "Initial run without creating sqlite file"
        #
        pipeline_run([test_task4], verbose = 0,
                     checksum_level = CHECKSUM_FILE_TIMESTAMPS,
                     multithread = 10,
                     one_second_per_job = one_second_per_job)

        #
        #   print "printout without sqlite"
        #
        s = StringIO()
        pipeline_printout(s, [test_task4], checksum_level = CHECKSUM_FILE_TIMESTAMPS)
        self.assertTrue(not re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue()))
        #
        # print "printout expecting sqlite file"
        #
        s = StringIO()
        pipeline_printout(s, [test_task4])
        self.assertTrue(re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue()))
        #
        #   print "Regenerate sqlite file"
        #
        pipeline_run([test_task4],
                     checksum_level = CHECKSUM_FILE_TIMESTAMPS,
                     history_file = get_default_history_file_name (),
                     multithread = 1,
                     verbose = 0,
                     touch_files_only = 2,
                     one_second_per_job = one_second_per_job)
        #
        # print "printout expecting sqlite file"
        #
        s = StringIO()
        pipeline_printout(s, [test_task4], verbose = VERBOSITY)
        succeed = not re.search('Tasks which will be run:.*\n(.*\n)*Task = ', s.getvalue())
        if not succeed:
            print(s.getvalue(), file=sys.stderr)
        self.assertTrue(succeed)

        throw_exception = False

    #___________________________________________________________________________
    #
    #   cleanup
    #___________________________________________________________________________
    def tearDown(self):
        shutil.rmtree(workdir)
        pass



#
#   Necessary to protect the "entry point" of the program under windows.
#       see: http://docs.python.org/library/multiprocessing.html#multiprocessing-programming
#
if __name__ == '__main__':
    #pipeline_printout(sys.stdout, [test_product_task], verbose = VERBOSITY)
    unittest.main()

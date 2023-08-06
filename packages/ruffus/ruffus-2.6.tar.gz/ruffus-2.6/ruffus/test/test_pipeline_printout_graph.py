#!/usr/bin/env python
from __future__ import print_function
"""

    test_split_subdivide_checkpointing.py


"""
tempdir = "testing_dir/"

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
for attr in "pipeline_run", "pipeline_printout_graph", "originate", "split", "transform", "subdivide", "formatter", "Pipeline":
    globals()[attr] = getattr (ruffus, attr)





#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   imports


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888


from subprocess import *



import unittest
import shutil

#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888

#   Each time the pipeline is FORCED to rerun,
#       More files are created for each task


#88888888888888888888888888888888888888888888888888888888888888888888888888888888888888888




@originate([tempdir + 'start'])
def make_start(outfile):
    """
    -> start
    """
    open(outfile, 'w').close()


@split(make_start, tempdir + '*.split')
def split_start(infiles, outfiles):
    """
    -> XXX.split
        where XXX = 0 .. N,
              N   = previous N + 1
    """

    # split always runs exactly one job (unlike @subdivide)
    # So it implicitly combines all its inputs before running and generating multiple output
    # @originate generates multiple output so the input for @split is a list...
    infile = infiles[0]

    # clean up previous
    for f in outfiles:
        os.unlink(f)


    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    #   Create more files than the previous invocation
    #
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    n_to_produce = len(outfiles) + 1
    for i in range(n_to_produce):
        f = '{}{}.split'.format(tempdir, i)
        open(f, 'a').close()



@subdivide(split_start, formatter(), tempdir + '{basename[0]}_*.subdivided', tempdir + '{basename[0]}')
def subdivide_start(infile, outfiles, infile_basename):
    # cleanup existing
    for f in outfiles:
        os.unlink(f)

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    #   Create more files than the previous invocation
    #
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    n_to_produce = len(outfiles) + 1
    for i in range(    n_to_produce):
        open('{}_{}.subdivided'.format(infile_basename, i), 'a').close()



class Test_ruffus(unittest.TestCase):

    def tearDown(self):
        # only tear down if not throw exception so we can debug?
        try:
            shutil.rmtree(tempdir)
        except:
            pass

    def setUp(self):
        try:
            shutil.rmtree(tempdir)
        except:
            pass
        os.makedirs(tempdir)

        #
        #   check graphviz exists for turning dot files into jpg, svg etc
        #
        try:
            process = Popen("echo what | dot", stdout=PIPE, stderr=STDOUT, shell = True)
            output, unused_err = process.communicate()
            retcode = process.poll()
            if retcode:
                raise CalledProcessError(retcode, "echo what | dot", output=output)
        except CalledProcessError as err:
            output_str = str(err.output)
            if "No such file or directory" in output_str or "not found" in output_str or "Unable to access jarfile"  in output_str:
                self.graph_viz_present = False
                return
        self.graph_viz_present = True

    def test_ruffus (self):

        print("     Run pipeline normally...")
        if self.graph_viz_present:
            pipeline_printout_graph(tempdir + "flowchart.dot")
            pipeline_printout_graph(tempdir + "flowchart.jpg",
                                        target_tasks =[subdivide_start],
                                        forcedtorun_tasks = [split_start],
                                        no_key_legend = True)
            pipeline_printout_graph(tempdir + "flowchart.svg", no_key_legend = False)
            # Unknown format
            try:
                pipeline_printout_graph(tempdir + "flowchart.unknown", no_key_legend = False)
                raise Exception("Failed to throw exception for pipeline_printout_graph unknown extension ")
            except CalledProcessError as err:
                pass
            pipeline_printout_graph(tempdir + "flowchart.unknown", "svg", no_key_legend = False)

        else:
            pipeline_printout_graph(tempdir + "flowchart.dot",
                                        target_tasks =[subdivide_start],
                                        forcedtorun_tasks = [split_start],
                                        no_key_legend = True)

    def test_newstyle_ruffus (self):

        print("     Run pipeline normally...")
        test_pipeline = Pipeline("test")
        test_pipeline.originate(make_start, [tempdir + 'start'])

        test_pipeline.split(split_start, make_start, tempdir + '*.split')

        test_pipeline.subdivide(subdivide_start, split_start, formatter(), tempdir + '{basename[0]}_*.subdivided', tempdir + '{basename[0]}')
        if self.graph_viz_present:
            test_pipeline.printout_graph(tempdir + "flowchart.dot")
            test_pipeline.printout_graph(tempdir + "flowchart.jpg",
                                        target_tasks =[subdivide_start],
                                        forcedtorun_tasks = [split_start],
                                        no_key_legend = True)
            test_pipeline.printout_graph(tempdir + "flowchart.svg", no_key_legend = False)
            # Unknown format
            try:
                test_pipeline.printout_graph(tempdir + "flowchart.unknown", no_key_legend = False)
                raise Exception("Failed to throw exception for test_pipeline.printout_graph unknown extension ")
            except CalledProcessError as err:
                pass
            test_pipeline.printout_graph(tempdir + "flowchart.unknown", "svg", no_key_legend = False)

        else:
            test_pipeline.printout_graph(tempdir + "flowchart.dot",
                                        target_tasks =[subdivide_start],
                                        forcedtorun_tasks = [split_start],
                                        no_key_legend = True)



if __name__ == '__main__':
    unittest.main()



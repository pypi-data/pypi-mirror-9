# coding: utf-8

from __future__ import unicode_literals, division

"""
TODO: Modify unittest doc.
"""


__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "12/31/13"

import unittest

from fireworks.user_objects.queue_adapters.common_adapter import *
from fireworks.utilities.fw_serializers import load_object, load_object_from_file

class CommonAdapterTest(unittest.TestCase):

    def test_serialization(self):
        p = CommonAdapter(
            q_type="PBS",
            q_name="hello",
            template_file=os.path.join(os.path.dirname(__file__),
                                       "mypbs.txt"),
                       hello="world", queue="random")
        p_new = load_object(p.to_dict())

        #Make sure the original and deserialized verison both work properly.
        for a in [p, p_new]:
            script = a.get_script_str("here")
            lines = script.split("\n")
            self.assertIn("# world", lines)
            self.assertIn("#PBS -q random", lines)

        p = CommonAdapter(
            q_type="PBS",
            q_name="hello",
            hello="world", queue="random")
        #this uses the default template, which does not have $${hello}
        self.assertNotEqual("# world", p.get_script_str("here").split("\n")[
            -1])
        self.assertNotIn("_fw_template_file", p.to_dict())

    def test_yaml_load(self):
        #Test yaml loading.
        p = load_object_from_file(os.path.join(os.path.dirname(__file__),
                              "pbs.yaml"))
        p = CommonAdapter(
            q_type="PBS",
            q_name="hello",
            ppnode="8:ib", nnodes=1,
            hello="world", queue="random")
        print(p.get_script_str("."))
        import yaml
        print(yaml.dump(p.to_dict(), default_flow_style=False))

    def test_parse_njobs(self):
        pbs = """
tscc-mgr.sdsc.edu:
                                                                                  Req'd    Req'd       Elap
Job ID                  Username    Queue    Jobname          SessID  NDS   TSK   Memory   Time    S   Time
----------------------- ----------- -------- ---------------- ------ ----- ------ ------ --------- - ---------
1039795.tscc-mgr.local  ongsp       home-ong test9             19382     1      8    --  240:00:00 R  35:08:40
1042879.tscc-mgr.local  ongsp       condo    test8             58416     1      8    --   08:00:00 R  03:31:41
1043137.tscc-mgr.local  whatever    home-ong test6               --      1      8    --  240:00:00 Q       -- """
        sge = """
job-ID  prior   name       user         state submit/start at     queue                          slots ja-task-ID
-----------------------------------------------------------------------------------------------------------------
  44275 10.55000 test3         ongsp        qw    12/31/2013 19:35:04     all.q                               8
  44275 10.55000 test4         ongsp        qw    12/31/2013 19:35:04     all.q                               8
  44275 10.55000 test5         ongsp        qw    12/31/2013 19:35:04     all.q                               8
"""
        p = CommonAdapter(
            q_type="PBS",
            q_name="hello",
            queue="home-ong",
            hello="world")
        self.assertEqual(p._parse_njobs(pbs, "ongsp"), 1)

        p = CommonAdapter(
            q_type="SGE",
            q_name="hello",
            queue="all.q",
            hello="world")
        self.assertEqual(p._parse_njobs(sge, "ongsp"), 3)

    def test_parse_jobid(self):
        p = CommonAdapter(
            q_type="SLURM",
            q_name="hello",
            queue="home-ong",
            hello="world")
        sbatch_output = """
SOME PREAMBLE
Submitted batch job 1234"""
        self.assertEqual(p._parse_jobid(sbatch_output), 1234)
        p = CommonAdapter(
                    q_type="PBS",
                    q_name="hello",
                    queue="home-ong",
                    hello="world")
        qsub_output = "2341.whatever"
        self.assertEqual(p._parse_jobid(qsub_output), '2341')
        p = CommonAdapter(
                    q_type="SGE",
                    q_name="hello",
                    queue="home-ong",
                    hello="world")
        qsub_output = "Your job 44275 (\"jobname\") has been submitted"
        self.assertEqual(p._parse_jobid(qsub_output), '44275')

if __name__ == '__main__':
    unittest.main()

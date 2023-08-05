import os
import unittest
from steps.bootstrap import Bootstrap
from steps.clean import Clean
from steps.utils import new_experiment
from steps.settings import EXPERIMENTS_FOLDER, PJ


class TestBase(unittest.TestCase):

    def setUp(self):
        """
        Set up of a test
        """
        self.dummy_name = "dummy"
        self.dummy_folder = PJ(EXPERIMENTS_FOLDER, self.dummy_name)
        if os.path.exists(self.dummy_folder):
            Clean(self.dummy_name).clean_all()
        self.dummy_exp = Bootstrap(
            self.dummy_name,
            repartition_dict={
                "border_router": 1,
                "coap_server": 7,
                "hello": 7
            }
        )

    def tearDown(self):
        """
        Set up the tear down for all the other suite
        """
        if os.path.exists(self.dummy_folder):
            Clean(self.dummy_name).clean_all()

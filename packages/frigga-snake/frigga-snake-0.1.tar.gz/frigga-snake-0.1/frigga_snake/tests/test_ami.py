from unittest import TestCase
from frigga_snake.ami import AMIName


class AMITestCase(TestCase):
    def test_correct_parsing(self):
        n = AMIName("livestats_scheduler-1-3-x86_64-2014-11-15T20-10-40Z", "name=livestats_scheduler, arch=x86_64, ancestor_name=base-nginx-image-2-1-x86_64-2014-10-15T06-57-30Z, ancestor_id=ami-4c4ce03b, ancestor_version=", "livestats_scheduler-1-3.h2067/livestats-project/2067")

        self.assertEqual(n.package_name, "livestats_scheduler")
        self.assertEqual(n.build_number, "h2067")
        self.assertEqual(n.version, "1")
        self.assertEqual(n.commit, "3")
        self.assertEqual(n.build_job_name, "livestats-project")
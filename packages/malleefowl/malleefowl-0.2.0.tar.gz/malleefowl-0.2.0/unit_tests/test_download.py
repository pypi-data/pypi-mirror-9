import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from os.path import basename

from __init__ import TESTDATA, CREDENTIALS

from malleefowl.download import download, download_with_archive, download_files

class DownloadTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.slp_1955_nc = "http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep.reanalysis.dailyavgs/surface/slp.1955.nc"
        cls.file_tasmax_nc = TESTDATA['tasmax_WAS-44_MPI-M-MPI-ESM-LR_historical_r1i1p1_MPI-CSC-REMO2009_v1_day_20010101-20051231.nc']
        cls.http_tasmax_nc = 'http://carbon.dkrz.de/thredds/fileServer/cordex/output/WAS-44/MPI-CSC/MPI-M-MPI-ESM-LR/historical/r1i1p1/MPI-CSC-REMO2009/v1/day/tasmax/v20140918/tasmax_WAS-44_MPI-M-MPI-ESM-LR_historical_r1i1p1_MPI-CSC-REMO2009_v1_day_20010101-20051231.nc'
        cls.http_pr_nc = 'http://carbon.dkrz.de/thredds/fileServer/cordex/output/EUR-44/CLMcom/MPI-M-MPI-ESM-LR/rcp85/r1i1p1/CLMcom-CCLM4-8-17/v1/day/pr/v20140424/pr_EUR-44_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_day_20110101-20151231.nc'
        
    @attr('online')
    def test_wget_download(self):
        result = download(self.slp_1955_nc)
        nose.tools.ok_(basename(result) == "slp.1955.nc", result)
        nose.tools.ok_(not 'file:///' in result, result)

    @attr('online')
    def test_wget_download_with_file_url(self):
        result = download(self.slp_1955_nc, use_file_url=True)
        nose.tools.ok_(basename(result) == "slp.1955.nc", result)
        nose.tools.ok_('file:///' in result, result)

    @attr('online')
    @attr('security')
    def test_download_with_creds(self):
        # TODO: configure path to wget
        raise SkipTest
        result = download(self.http_pr_nc, CREDENTIALS)
        nose.tools.ok_(
            basename(result) == "pr_EUR-44_MPI-M-MPI-ESM-LR_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_day_20110101-20151231.nc",
            result)

    @attr('online')
    def test_download_with_archive(self):
        # TODO: configure archive path
        raise SkipTest
        result = download_with_archive(self.http_tasmax_nc)
        nose.tools.ok_(
            basename(result) == "tasmax_WAS-44_MPI-M-MPI-ESM-LR_historical_r1i1p1_MPI-CSC-REMO2009_v1_day_20010101-20051231.nc",
            result)

    @attr('online')
    def test_download_files(self):
        results = download_files(urls=[self.slp_1955_nc])
        nose.tools.ok_(len(results) == 1, results)
        
        


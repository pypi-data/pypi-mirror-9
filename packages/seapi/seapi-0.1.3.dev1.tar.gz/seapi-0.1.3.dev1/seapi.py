"""
Class for connecting to the Silicon Expert API and searching on a single mpn,mfr combination

e. g.
search = SiliconExpertSearch_MPN_MFR(mpn='bav99',mfr='Fairchild')
search.get_list_result('comid')
search.get_detail_result(comid,'TaxonomyPath')
comid = search.comid
taxonomy = search.TaxonomyPath
"""

__author__ = 'Richard Rymer'

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import urllib
import urllib2
import cookielib


class SearchError(object):
    def __init__(self,mpn,mfr,error,reporting=False):
        self.mpn = mpn
        self.mfr = mfr
        self.error = error
        self.reporting = reporting

    def report(self):
        if self.reporting:
            print self.mpn,self.mfr,self.error

    def __nonzero__(self):
        if isinstance(self.error,str):
            return False
        elif self.error is True:
            return True
        return False

class SiliconExpertSearch_MPN_MFR(object):
    def __init__(self,mpn=None,mfr=None,verbose=False,logger=None):
        """
        Initializes a Silicon Expert search object
        :param mpn: string
        :param mfr: string
        :return:object
        """
        self.mpn = mpn
        self.mfr = mfr
        self.verbose = verbose
        self.logger=logger
        self.list_url="""https://app.siliconexpert.com/SearchService/search/listPartSearch?partNumber=[{"""+urllib.urlencode({'partNumber':self.mpn})+','+urllib.urlencode({'manufacturer':self.mfr})+"""}]&fmt=xml"""
        self.detail_url = "https://app.siliconexpert.com/SearchService/search/partDetail?comIds={}&fmt=xml"
        self.part_search_url =  "https://app.siliconexpert.com/SearchService/search/partsearch?{}&fmt=xml"
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        self.list_results=None
        self.detail_results=None
        self.part_search_results=None
        self.i = 0
    
    def _authenticate(self,tries=0):
        """
        Authenticates a session with the Silicon Expert search API
        :param tries: int
        :return:None
        """
        
        username = raw_input("username:")
        password = raw_input("password:")
        results = self.opener.open(\
            "https://app.siliconexpert.com/SearchService/search/authenticateUser?login={0}&apiKey={1}".format(username, password))
        while not self._check_results(results.read()) and tries <= 10:
            results = self.opener.open(\
                "https://app.siliconexpert.com/SearchService/search/authenticateUser?login={0}&apiKey={1}".format(username, password))
            tries += 1
    
    def _check_results(self,results):
        """
        Checks the results of a search or url opening to verify they/it succeeded
        :param results: object
        :return: bool
        """
        if isinstance(results,bool) or results is None:
            error = results
        elif isinstance(results,BeautifulSoup):
            error = results.success.string == 'true'
        elif isinstance(results,ET.Element):
            error = results.find('Status').find('Success').text == 'true'
        else:
            parsed_results = self._parse_xml_results(results)
            if parsed_results is None:
                error = 'Parse Error'
            elif parsed_results.find('Status').find('Message').text == 'Authentication Succeeded':
                error = True
            elif parsed_results.find('Status').find('Success').text == 'true':
                error = True
            elif parsed_results.find('Status').find('Message').text == 'Invalid User Name Or Password':
                self._authenticate()
                error = "Authentication Error"
            elif parsed_results.find('Status').find('Success').text == 'false' and\
                    parsed_results.find('Status').find('Message').text == "Wrong COM ID(s)":
                error = 'Wrong Comid'
            elif parsed_results.find('Status').find('Success').text == 'false' and\
                    parsed_results.find('Status').find('Message').text == "No Results Found":
                error = "No Results Found"
            elif parsed_results.find('Status').find('Success').text == 'false':
                error = 'something else failed:' + str(results)
            else:
                raise RuntimeError, 'This not supposed to happen:' + str(results)
        return SearchError(self.mpn,self.mfr,error,reporting=self.verbose)
    
    def _parse_html_results(self,raw_results):
        """
        Parses the raw html output
        :param raw_results: list
        :return: object
        """
        return BeautifulSoup(''.join(raw_results))
    
    def _parse_xml_results(self,raw_results):
        """
        Parses the xml in raw_results
        :param raw_results: str
        :return: object
        """
        while self.i <= 10:
            try:
                return ET.fromstring(''.join(raw_results))
            except ET.ParseError:
                self.i += 1
                continue
            
    def _run_list_search(self):
        """
        Performs a list part search
        :param i: int
        :return:object
        """
        self.i += 1
        r = self.opener.open(self.list_url)
        results = r.read()
        self.results_check = self._check_results(results)
        if not self.results_check and self.i <= 10:
            if self.results_check.error == "No Results Found":
                return False
            return self._run_list_search()
        return self._parse_html_results(results)
    
    def _run_detail_search(self,comid):
        """
        Performs a part detail search
        :param comid: str
        :param i: int
        :return:object
        """
        self.i += 1
        r = self.opener.open(self.detail_url.format(comid))
        results = r.read()
        self.results_check = self._check_results(results)
        if not self.results_check and self.i <= 10:
            if self.results_check.error == "No Results Found":
                return False
            elif self.results_check == "Wrong Comid":
                return False
            return self._run_list_search()
        return self._parse_xml_results(results)

    def _run_part_search(self,mfr):
        """
        Performs a part detail search
        :param comid: str
        :param i: int
        :return:object
        """
        self.i += 1
        search_term = self.mpn + '{}'.format(' ' + self.mfr if mfr else '')
        r = self.opener.open(self.part_search_url.format(urllib.urlencode({'partNumber':search_term})))
        results = r.read()
        self.results_check = self._check_results(results)
        if not self.results_check and self.i <= 10:
            if self.results_check.error == "No Results Found":
                return False
            return self._run_part_search(mfr)
        return self._parse_xml_results(results)

    def _store_search_results(self,results_name,results_value):
        """
        Stores the results of a search as an attribute of the search object
        :param results_name: str
        :param results_value: str
        :return:None
        """
        setattr(self,results_name,results_value)

    def get_list_result(self,field,raw=False):
        """
        Returns the value of a single field in a part list search.
        Specifying raw=True will return the raw results object
        :param field: str
        :param raw: bool
        :return: str
        """
        if not self.list_results:
            self.list_results = self._run_list_search()
        if raw:
            return self.list_results
        if self._check_results(self.list_results):
            try:
                self._store_search_results(field,getattr(getattr(self.list_results,field),'string'))
                return True
            except AttributeError:
                try:
                    self._store_search_results(field,getattr(self.list_results,field))
                    return True
                except AttributeError:
                    pass
        else:
            pass
        return False
    
    def get_detail_result(self,comid,field,raw=False):
        """
        Returns the value of a single field in a part detail search.
        Specifying raw=True will return the raw results object
        :param comid:str
        :param field:str
        :param raw:bool
        :return:str
        """
        if not self.detail_results:
            self.detail_results = self._run_detail_search(str(comid))
        if raw:
            return self.detail_results
        elif self._check_results(self.detail_results):
            for child_field in self.detail_results.find('Results').find('ResultDto'):
                if child_field.find(field) is not None:
                    self._store_search_results(field,child_field.find(field).text)
                    return True
        else:
            pass
        return False

    def get_part_search_results(self,field,mfr=True,raw=False):
        """
        Returns the value of a single field in a part keyword search.
        Specifying mfr=False will perform the search without the mfr attribute
        Specifying raw=True will return the raw results object
        :param field:str
        :param mfr:bool
        :param raw:bool
        :return:str
        """
        if not self.part_search_results:
            self.part_search_results = self._run_part_search(mfr)
        if raw:
            return self.part_search_results
        elif self._check_results(self.part_search_results):
            self._store_search_results(field,[result.find(field).text for result in\
                    self.part_search_results.findall('Result') if result.find(field) is not None])
            return True
        else:
            pass
        return False


def test1():
    """
    Verifies that
    1) A connection to the API can be established and authenticated.
    2) A part list search will return a comid that can be successfully used to
    3) return a part taxonomy in a part detail search.
    :return:print "Connection established"
    """
    search = SiliconExpertSearch_MPN_MFR(mpn='bav99',mfr='Fairchild')
    assert search.get_list_result('comid')
    assert search.comid == '18508781', search.comid
    assert isinstance(search.results_check,SearchError)
    assert isinstance(search.results_check.error,bool)
    assert search.get_detail_result(search.comid,'TaxonomyPath')
    assert search.TaxonomyPath == 'Diodes, Transistors and Thyristors > Rectifiers > Rectifier', search.TaxonomyPath
    assert search.get_part_search_results('ComID',mfr=False)
    assert search.comid in search.ComID, search.ComID
    print "Connection established"

def test2():
    """
    Verifies that an incorrect search will return None only once
    :return:print "No Results Found"
    """
    search = SiliconExpertSearch_MPN_MFR(mpn='blah',mfr='Does not exist')
    assert not search.get_list_result('comid')
    assert search.results_check.error == "No Results Found"
    assert search.i <= 2, str(search.i)

if __name__ == '__main__':
    test1()
    test2()

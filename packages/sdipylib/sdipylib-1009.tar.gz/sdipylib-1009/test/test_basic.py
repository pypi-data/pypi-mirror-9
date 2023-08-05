import unittest

class TestBase(unittest.TestCase):
    
    
    def test_basic(self):
        from sdipylib.url import cache_url
        
        x = 's3://restricted.sandiegodata.org/manifests/7a007ac7-960f-468b-8ce3-7b9f83e34ea8/hnr0914.csv'
        
        print cache_url(x)
        
if __name__ == '__main__':
    unittest.main()
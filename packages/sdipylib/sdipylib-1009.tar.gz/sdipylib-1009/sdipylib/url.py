"""Functions for loading and saving URLS"""

import requests
def cache_url(url):
    """Load a url to a local file, or return the file path  if it already exists
    This function will download the given URL to the current directory, with a file name of the
    last path element in the URL. 
    
    
    """
    import os
    import urlparse
    from IPython.display import display, clear_output
    import sys
    
    parts = urlparse.urlparse(url)
    
    if not parts.scheme in ['http','https', 'ftp', 's3']:
        raise Exception("Probably not a valid URL")
    
    verify = True
    if parts.scheme == 's3':
        import boto
        # Convert it into an expiring URL and use the normal process. 
        conn = boto.connect_s3()
        b = conn.get_bucket(parts.netloc)
        k = boto.s3.key.Key(b)
        k.key = parts.path
        url = k.generate_url(60)
        verify = False # Hostnames never match cert
    
    # Return the file directly if it already exists
    fn = os.path.basename(parts.path)
    if os.path.exists(fn):
        return os.path.abspath(fn)
    
    r = requests.get(url, stream=True, verify=verify)

    r.raise_for_status()

    total = 0
    with open(fn, 'wb') as fd:
        for chunk in r.iter_content(2**20): # Read about 1MB, final len() is longer because of decompression
            fd.write(chunk)
            clear_output(wait=True)
            total += len(chunk)
            print "Wrote {} bytes, total {}".format(len(chunk), total)
            sys.stdout.flush()
            
    return os.path.abspath(fn)

def download_ambry_db(url,name=None):  
    """Download an Ambry database file from the repository. """
    import gzip
    import sys
    import os
    
    if not name:
        name = os.path.basename(url)
    
    if not os.path.exists(name+'.gz'):
        print 'Downloading:', url
        sys.stdout.flush()
        import urllib
        urllib.urlretrieve (url, name+'.gz')
    else:
        print 'Already downloaded:', url
        sys.stdout.flush()

    if not os.path.exists(name):
        print 'Extracting to:',name
        sys.stdout.flush()
        with open(name,'wb') as out_f, gzip.open(name+'.gz', 'rb') as in_f:
            out_f.write(in_f.read())   
    else:
        print 'Already extracted:', name
        sys.stdout.flush()

    

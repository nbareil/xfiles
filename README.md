
xfiles
======

xfiles is a simple HTTP file transfer server. Clients can upload files
which will be stored encrypted (using GnuPG symetric encryption).

Cipher key is never stored on server side. Key is handled to the clients
through the download URL like this one : 

    http://example.com/download/2fbnnZNXljkX2Hxr#hhYowmvPiwSNa55X8px9oGbyPPxVaWYo

Where:

 - 2fbnnZNXljkX2Hxr is the requested filename
 - hhYowmvPiwSNa55X8px9oGbyPPxVaWYo is the encryption key

requirements
============

 - python-gnupg (>= v0.2.9)
 - web.py (>= 0.3)
 

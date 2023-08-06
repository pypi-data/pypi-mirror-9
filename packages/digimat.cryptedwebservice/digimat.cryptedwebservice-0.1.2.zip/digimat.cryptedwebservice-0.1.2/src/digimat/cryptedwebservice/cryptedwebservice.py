import requests
import base64
import struct

from xml.dom import minidom
import traceback

# pip install pycrypto (compiling may fails, see second option below)
# apt-get install python-crypto
from Crypto.Cipher import Blowfish


class CryptedWebservice(object):
    def __init__(self, url, device, key):
        self._url=url
        self._device=device
        self._key=key

    def encrypt(self, data):
        try:
            bf=Blowfish.BlowfishCipher(self._key)
            bs=Blowfish.block_size
            psize=bs-divmod(len(data),bs)[1]
            if psize:
                data=data+'\0'*psize
            return base64.b64encode(bf.encrypt(data))
        except:
            pass

    def decrypt(self, data):
        try:
            bf=Blowfish.BlowfishCipher(self._key)
            return bf.decrypt(base64.b64decode(data)).rstrip()
        except:
            pass

    def do(self, command, data=None):
        payload={'device':self._device, 'command':command}
        if data:
            cdata=self.encrypt(data)
            payload['data']=cdata
        try:
            r=requests.post(self._url, params=payload, timeout=10)
            if r.status_code==200:
                #print r.text.encode('utf-8')
                try:
                    data=self.decrypt(r.text).strip()
                    #print data
                    return minidom.parseString(data).documentElement
                except:
                    pass
        except:
            pass

    def isResponseSuccess(self, xresponse):
        try:
            if xresponse:
                node=xresponse.firstChild
                while node:
                    if node.nodeType==minidom.Node.ELEMENT_NODE:
                        name=node.nodeName.lower()
                        if name=='success':
                            return node
                    node=node.nextSibling
        except:
            #traceback.print_exc()
            pass

    def doAndCheckSuccess(self, command, data):
        xresponse=self.do(command, data)
        return self.isResponseSuccess(xresponse)

    def ping(self):
        xresponse=self.do('ping')
        if self.isResponseSuccess(xresponse):
            return True

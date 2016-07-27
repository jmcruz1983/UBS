"""
Module that loads properties from a file

Originally created by - Anand B Pillai <abpillai@gmail.com>
Modified by - Juan Cruz <jmcruz1983@gmail.com>
"""

import re
import sys
import time
import os.path

_propCache = {}

def loadProperties(fileName):
    if _propCache.has_key(fileName):
        return _propCache[fileName]
    p = Properties()
    filepath = os.path.join(os.getcwd(), fileName)
    p.load(open(filepath))

    _propCache[fileName] = p
    return p

class IllegalArgumentException(Exception):

    def __init__(self, lineno, msg):
        self.lineno = lineno
        self.msg = msg

    def __str__(self):
        s='Exception at line number %d => %s' % (self.lineno, self.msg)
        return s

class Properties(object):
    """ A Python replacement for java.util.Properties """

    def __init__(self, props=None):
        # Dictionary of properties.
        self._props = {}
        # Dictionary of properties with 'pristine' keys
        # This is used for dumping the properties to a file
        # using the 'store' method
        self._origprops = {}

        # Dictionary mapping keys from property
        # dictionary to pristine dictionary
        self._keymap = {}

        self.othercharre = re.compile(r'(?<!\\)(\s*\=)|(?<!\\)(\s*\:)')
        self.othercharre2 = re.compile(r'(\s*\=)|(\s*\:)')
        self.bspacere = re.compile(r'\\(?!\s$)')

    def __str__(self):
        s='{'
        for key,value in self._props.items():
            s = ''.join((s,key,'=',value,', '))

        s=''.join((s[:-2],'}'))
        return s

    def __parse(self, lines):
        """ Parse a list of lines and create
        an internal property dictionary """

        lineno=0
        i = iter(lines)

        for line in i:
            lineno += 1
            line = line.strip()
            # Skip null lines
            if not line: continue
            # Skip lines which are comments
            if line[0] == '#': continue
            # Position of first separation char
            sepidx = -1
            # Check for valid space separation
            # First obtain the max index to which we
            # can search.
            m = self.othercharre.search(line)
            if m:
                first, last = m.span()
                start, end = 0, first
                wspacere = re.compile(r'(?<![\\\=\:])(\s)')
            else:
                if self.othercharre2.search(line):
                    # Check if either '=' or ':' is present
                    # in the line. If they are then it means
                    # they are preceded by a backslash.

                    # This means, we need to modify the
                    # wspacere a bit, not to look for
                    # : or = characters.
                    wspacere = re.compile(r'(?<![\\])(\s)')
                start, end = 0, len(line)

            m2 = wspacere.search(line, start, end)
            if m2:
                # print 'Space match=>',line
                # Means we need to split by space.
                first, last = m2.span()
                sepidx = first
            elif m:
                # print 'Other match=>',line
                # No matching wspace char found, need
                # to split by either '=' or ':'
                first, last = m.span()
                sepidx = last - 1

            # If the last character is a backslash
            # it has to be preceded by a space in which
            # case the next line is read as part of the
            # same property
            while line[-1] == '\\':
                # Read next line
                nextline = i.next()
                nextline = nextline.strip()
                lineno += 1
                # This line will become part of the value
                line = line[:-1] + nextline

            # Now split to key,value according to separation char
            if sepidx != -1:
                key, value = line[:sepidx], line[sepidx+1:]
            else:
                key,value = line,''

            self.processPair(key, value)

    def processPair(self, key, value):
        """ Process a (key, value) pair """
        oldkey = key
        oldvalue = value

        # Create key intelligently
        keyparts = self.bspacere.split(key)
        # print keyparts

        strippable = False
        lastpart = keyparts[-1]

        if lastpart.find('\\ ') != -1:
            keyparts[-1] = lastpart.replace('\\','')

        # If no backspace is found at the end, but empty
        # space is found, strip it
        elif lastpart and lastpart[-1] == ' ':
            strippable = True

        key = ''.join(keyparts)
        if strippable:
            key = key.strip()
            oldkey = oldkey.strip()

        oldvalue = self.unescape(oldvalue)
        value = self.unescape(value)

        self._props[key] = value.strip()

        # Check if an entry exists in pristine keys
        if self._keymap.has_key(key):
            oldkey = self._keymap.get(key)
            self._origprops[oldkey] = oldvalue.strip()
        else:
            self._origprops[oldkey] = oldvalue.strip()
            # Store entry in keymap
            self._keymap[key] = oldkey

    def escape(self, value):
        # Java escapes the '=' and ':' in the value
        # string with backslashes in the store method.
        # So let us do the same.
        newvalue = value.replace(':','\:')
        newvalue = newvalue.replace('=','\=')
        return newvalue

    def unescape(self, value):
        # Reverse of escape
        newvalue = value.replace('\:',':')
        newvalue = newvalue.replace('\=','=')
        return newvalue

    def load(self, stream):
        """ Load properties from an open file stream """

        # For the time being only accept file input streams
        if type(stream) is not file:
            raise TypeError,'Argument should be a file object!'
        # Check for the opened mode
        if stream.mode != 'r':
            raise ValueError,'Stream should be opened in read-only mode!'

        try:
            lines = stream.readlines()
            self.__parse(lines)
        except IOError:
            raise

    def getProperty(self, key):
        """ Return a property for the given key """
        return self._props.get(key,'')

    def setProperty(self, key, value):
        """ Set the property for the given key """
        if type(key) is str and type(value) is str:
            self.processPair(key, value)
        else:
            raise TypeError,'both key and value should be strings!'

    def propertyNames(self):
        """ Return an iterator over all the keys of the property
        dictionary, i.e the names of the properties """
        return self._props.keys()

    def list(self, out=sys.stdout):
        """ Prints a listing of the properties to the
        stream 'out' which defaults to the standard output """
        out.write('-- listing properties --\n')
        for key,value in self._props.items():
            out.write(''.join((key,'=',value,'\n')))

    def store(self, out, header=""):
        """ Write the properties list to the stream 'out' along
        with the optional 'header' """
        if out.mode[0] != 'w':
            raise ValueError,'Steam should be opened in write mode!'

        try:
            out.write(''.join(('#',header,'\n')))
            # Write timestamp
            tstamp = time.strftime('%a %b %d %H:%M:%S %Z %Y', time.localtime())
            out.write(''.join(('#',tstamp,'\n')))
            # Write properties from the pristine dictionary
            for prop, val in self._origprops.items():
                out.write(''.join((prop,'=',self.escape(val),'\n')))

            out.close()
        except IOError:
            raise

    def getPropertyDict(self):
        return self._props

    def __getitem__(self, name):
        """ To support direct dictionary like access """
        return self.getProperty(name)

    def __setitem__(self, name, value):
        """ To support direct dictionary like access """
        self.setProperty(name, value)

    def __getattr__(self, name):
        """ For attributes not found in self, redirect
        to the properties dictionary """

        try:
            return self.__dict__[name]
        except KeyError:
            if hasattr(self._props,name):
                return getattr(self._props, name)

if __name__=="__main__":
    propfilepath = os.path.abspath(
        os.path.join(
            os.getcwd(),
            'service.properties'))
    if not os.path.exists(propfilepath):
        open(propfilepath,'w').close()
    p = Properties()
    p.load(open(propfilepath))
    p.list()
    p['prop1'] = 'v1'
    p['prop2'] = str(time.clock())
    p.store(open(propfilepath,'w'))
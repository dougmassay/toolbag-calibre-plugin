# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

from collections import OrderedDict
import regex as re

SVG_ATTR = ['attributeName', 'attributeType', 'baseFrequency', 'baseProfile', 'calcMode', 'clipPathUnits', 'contentScriptType', 'contentStyleType',
            'diffuseConstant', 'edgeMode', 'externalResourcesRequired', 'filterRes', 'filterUnits', 'glyphRef', 'gradientTransform', 'gradientUnits',
            'kernelMatrix', 'kernelUnitLength', 'keyPoints', 'keySplines', 'keyTimes', 'lengthAdjust', 'limitingConeAngle', 'markerHeight', 'markerUnits',
            'markerWidth', 'maskContentUnits', 'maskUnits', 'numOctaves', 'pathLength', 'patternContentUnits', 'patternTransform', 'patternUnits',
            'pointsAtX', 'pointsAtY', 'pointsAtZ', 'preserveAlpha', 'preserveAspectRatio', 'primitiveUnits', 'refX', 'refY', 'repeatCount', 'repeatDur',
            'requiredExtensions', 'requiredFeatures', 'specularConstant', 'specularExponent', 'spreadMethod', 'spreadMethod', 'startOffset', 'stdDeviation',
            'stitchTiles', 'surfaceScale', 'systemLanguage', 'tableValues', 'targetX','targetY', 'textLength', 'viewBox', 'viewTarget', 'xChannelSelector',
            'yChannelSelector', 'zoomAndPan']

def attrMatch(attr_str, method, srch_str):
    if method == 'normal':
        return (attr_str == srch_str)
    elif method == 'regex':
        if re.match(r"""%s""" % srch_str, attr_str, re.U) is not None:
            return True
        else:
            return False

class MarkupParser(object):
    def __init__(self, data, srch_str=None, srch_method='normal', tag='span', attrib='class', action='delete', new_tag=None,  new_str='', copy=False):
        self.wipml = data
        self.pos = 0
        self.path = []
        self.tag = tag
        self.new_tag = new_tag
        self.attrib = attrib
        self.srch_str = srch_str
        self.srch_method = srch_method
        self.action = action
        self.new_str = new_str
        self.copy_attr = copy

    def parse_new_tattr(self, s, p=0):
        tattr = {}
        while s.find('=',p) != -1 :
            while s[p:p+1] == ' ' : p += 1
            b = p
            while s[p:p+1] != '=' : p += 1
            aname = s[b:p]
            if aname.strip() not in SVG_ATTR:
                aname = aname.lower()
            aname = aname.rstrip(' ')
            p += 1
            while s[p:p+1] == ' ' : p += 1
            if s[p:p+1] == '"' :
                p = p + 1
                b = p
                while s[p:p+1] != '"': p += 1
                val = s[b:p]
                p += 1
            else :
                b = p
                while s[p:p+1] not in ('>', '/', ' ') : p += 1
                val = s[b:p]
            tattr[aname] = val
        return tattr

    # parse leading text of xhtml and tag
    def parseml(self):
        p = self.pos
        if p >= len(self.wipml):
            return None
        if self.wipml[p] != '<':
            res = self.wipml.find('<',p)
            if res == -1 :
                res = len(self.wipml)
            self.pos = res
            return self.wipml[p:res], None
        # handle comment as a special case
        # deal with even multipline comments properly
        # don't parse code in in between
        if self.wipml[p:p+4] == '<!--':
            te = self.wipml.find('-->',p+1)
            if te != -1:
                te = te+2
        else :
            tb = p
            te = self.wipml.find('>',p+1)
            ntb = self.wipml.find('<',p+1)
            if ntb != -1 and ntb < te:
                self.pos = ntb
                return self.wipml[p:ntb], None
        self.pos = te + 1
        return None, self.wipml[p:te+1]

    # parses string version of tag to identify its name,
    # its type 'begin', 'end' or ('single'|'single_ext'),
    # plus build a hashtable of its atributes
    # code is written to handle the possiblity of very poor formating
    def parsetag(self, s):
        p = 1
        # get the tag name
        tname = None
        ttype = None
        tattr = None
        while s[p:p+1] == ' ' : p += 1
        if s[p:p+1] == '/':
            ttype = 'end'
            p += 1
            while s[p:p+1] == ' ' : p += 1
        b = p
        while s[p:p+1] not in ('>', '/', ' ', '"', "\r", "\n") : p += 1
        tname=s[b:p].lower()
        # some special cases
        if tname == "!--":
            ttype = 'passthru'
            info = s[p:-3]
            tattr = {}
            tattr['info'] = info
        if tname == "!doctype":
            tname = "!DOCTYPE"
            ttype = 'passthru'
            info = s[p:-1]
            tattr = {}
            tattr['info'] = info
        if tname == "![cdata[*":
            tname = "![CDATA[*"
            ttype = 'passthru'
            info = s[p:-1]
            tattr = {}
            tattr['info'] = info
        if tname == "svg":
            if ttype == 'end':
                ttype = 'passthru-end'
            else:
                ttype = 'passthru'
            info = s[p:-1]
            tattr = {}
            tattr['info'] = info
        if tname.startswith("?"):
            ttype = 'passthru'
            info = s[p:-2]
            tattr = {}
            tattr['info'] = info

        if ttype is None:
            # parse any attributes
            # tattr = {}
            # tattr = self.parse_attr(s,p)

            tattr = OrderedDict()
            while s.find('=',p) != -1 :
                while s[p:p+1] in (' ', '\r', '\n') : p += 1
                b = p
                while s[p:p+1] != '=' : p += 1
                aname = s[b:p]
                if aname.strip() not in SVG_ATTR:
                    aname = aname.lower()
                aname = aname.rstrip()
                p += 1
                while s[p:p+1] == ' ' : p += 1
                if s[p:p+1] == '"' :
                    p = p + 1
                    b = p
                    while s[p:p+1] != '"': p += 1
                    val = s[b:p]
                    p += 1
                else :
                    b = p
                    while s[p:p+1] not in ('>', '/', ' ') : p += 1
                    val = s[b:p]
                tattr[aname] = val

        if tattr and len(tattr)== 0: tattr = None

        # label beginning and single tags
        if not ttype:
            ttype = 'begin'
            if s.find(' /',p) >= 0:
                ttype = 'single_ext'
            elif s.find('/',p) >= 0:
                ttype = 'single'

        return ttype, tname, tattr

    # main routine to process the xhtml markup language
    def processml(self):
        htmlstr = ''
        skip = False

        # now parse the cleaned up ml into standard xhtml
        while True:

            r = self.parseml()
            if not r:
                break

            text, tag = r

            if text:
                if not skip:
                    htmlstr += text

            if tag:
                ttype, tname, tattr = self.parsetag(tag)

                # mark any tags to remove/modify
                if self.attrib is not None: # Tags with attributes
                    if tname == self.tag and ttype in ('begin', 'single', 'single_ext') and self.attrib in tattr.keys() and attrMatch(tattr[self.attrib], self.srch_method, self.srch_str):
                        if self.action == 'delete':
                            tname = 'removeme:{0}'.format(tname)
                            tattr = None
                        elif self.action == 'modify':
                            if self.new_tag is None:
                                tname = 'changeme:{0}'.format(tname)
                            else:
                                tname = 'changeme:{0}'.format(self.new_tag)
                            if not self.copy_attr:
                                if not len(self.new_str):
                                    tattr = None
                                else:
                                    tattr = self.parse_new_tattr(self.new_str)
                else:  # Tags without any attributes
                    if tname == self.tag and ttype in ('begin', 'single', 'single_ext') and not len(tattr):
                        if self.action == 'delete':
                            tname = 'removeme:{0}'.format(tname)
                            tattr = None
                        elif self.action == 'modify':
                            if self.new_tag is None:
                                tname = 'changeme:{0}'.format(tname)
                            else:
                                tname = 'changeme:{0}'.format(self.new_tag)
                            if not len(self.new_str):
                                tattr = None
                            else:
                                tattr = self.parse_new_tattr(self.new_str)

                if tname == self.tag and ttype == 'end':
                    if self.action == 'delete':
                        if self.path[-1] == 'removeme:{0}'.format(tname):
                            tname = 'removeme:{0}'.format(tname)
                            tattr = None
                    elif self.action == 'modify':
                        if self.new_tag is None:
                            if self.path[-1] == 'changeme:{0}'.format(tname):
                                tname = 'changeme:{0}'.format(tname)
                        else:
                            if self.path[-1] == 'changeme:{0}'.format(self.new_tag):
                                tname = 'changeme:{0}'.format(self.new_tag)
                        tattr = None

                # keep track of nesting path
                # special case xml doctype
                # if ttype == 'begin' and tname != '?xml' and tname != '!DOCTYPE':
                # should not need the previous if ttype cannot possibly equal both 'begin' and 'passthrough'.
                if ttype == 'begin':
                    self.path.append(tname)
                elif ttype == 'end':
                    if tname != self.path[-1]:
                        print ('improper nesting: ', self.path, tname, type)
                    self.path.pop()

                if tname == 'removeme:{0}'.format(tname):
                    if ttype in ('begin', 'single', 'single_ext'):
                        skip = True
                    else:
                        skip = False
                else:
                    taginfo = (ttype, tname, tattr)
                    htmlstr += self.processtag(taginfo)

        return htmlstr

    # flatten possibly modified tag back to string
    def taginfo_tostring(self, taginfo):
        (ttype, tname, tattr) = taginfo
        res = '<'
        if ttype == 'end':
            res += '/' + tname + '>'
            return res
        res += tname
        if tattr:
            for key in tattr.keys():
                res += ' '
                res += key + '="'
                res += tattr[key] + '"'
            res == ' '
        if ttype == 'single':
            res += '/>'
        elif ttype == 'single_ext':
            res += ' />'
        else :
            res += '>'
        return res

    # routines to allow preprocessing and conversion of tags
    def processtag(self, taginfo):

        # current tag to work on
        (ttype, tname, tattr) = taginfo

        # put any code here to manipulate or process tags

        if tname is None or tname.startswith('removeme'):
            return ''
        if tname.startswith('changeme'):
            tname = tname[9:]
        if tattr is None:
            tattr = {}

        # handle passthru special cases
        if ttype.startswith('passthru'):
            if tname == '!--':
                return '<!--{0}-->'.format(tattr.get('info',' '))
            if tname == '!DOCTYPE':
                return '<!DOCTYPE{}>'.format(tattr.get('info',''))
            if tname == '![CDATA[*':
                return '<![CDATA[*{}>'.format(tattr.get('info',''))
            if tname == 'svg':
                if ttype == 'passthru-end':
                    return '</svg>'
                return '<svg{}>'.format(tattr.get('info',''))
            if tname.startswith('?'):
                return "<{0}{1}?>".format(tname, tattr.get('info',''))

        # add your own processing of tags here

        # convert updated tag back to string representation
        if len(tattr) == 0: tattr = None
        taginfo = (ttype, tname, tattr)
        return self.taginfo_tostring(taginfo)

#-*- coding: utf-8 -*-
#
# Created on Dec 17, 2012
#
# @author: Younes JAAIDI
#
# $Id: 41aec73343abad123c96801fbf66a84ac5e38274 $
#

from .i_naming_convention import INamingConvention

class NamingConventionCamelCase(INamingConvention):
    
    def getterName(self, memberName):
        return memberName
    
    def setterName(self, memberName):
        memberNameFirstLetter = memberName[:1].upper()
        memberNameEnd = memberName[1:]
        return 'set%s%s' % (memberNameFirstLetter, memberNameEnd)

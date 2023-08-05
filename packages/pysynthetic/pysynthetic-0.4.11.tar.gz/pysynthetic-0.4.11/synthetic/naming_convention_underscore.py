#-*- coding: utf-8 -*-
#
# Created on Dec 17, 2012
#
# @author: Younes JAAIDI
#
# $Id: e5752b7b3a048cb12479dfa5572bcaa619c7daed $
#

from .i_naming_convention import INamingConvention

class NamingConventionUnderscore(INamingConvention):
    
    def getterName(self, memberName):
        return memberName
    
    def setterName(self, memberName):
        return 'set_%s' % memberName

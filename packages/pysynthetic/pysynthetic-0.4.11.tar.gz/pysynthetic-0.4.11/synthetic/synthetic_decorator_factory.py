#-*- coding: utf-8 -*-
#
# Created on Dec 17, 2012
#
# @author: Younes JAAIDI
#
# $Id: d5df9617e7864700e607f3e341fe91ba0bad99af $
#

from .i_member_delegate import IMemberDelegate
from .i_naming_convention import INamingConvention
from .synthetic_class_controller import SyntheticClassController
from .synthetic_member import SyntheticMember
from contracts import contract, new_contract

new_contract('IMemberDelegate', IMemberDelegate)
new_contract('INamingConvention', INamingConvention)
new_contract('SyntheticMember', SyntheticMember)

class SyntheticDecoratorFactory:

    @contract
    def syntheticMemberDecorator(self,
                                 memberName,
                                 defaultValue,
                                 contract,
                                 readOnly,
                                 privateMemberName,
                                 memberDelegate):
        """
    :type memberName: str
    :type readOnly: bool
    :type privateMemberName: str|None
    :type memberDelegate: IMemberDelegate
"""
        def decoratorFunction(cls):
            syntheticMember = SyntheticMember(memberName,
                                              defaultValue,
                                              contract,
                                              readOnly,
                                              privateMemberName,
                                              memberDelegate = memberDelegate)

            SyntheticClassController(cls).addSyntheticMember(syntheticMember)

            return cls
        return decoratorFunction

    def syntheticConstructorDecorator(self):
        def functionWrapper(cls):            
            # This will be used later to tell the new constructor to consume parameters to initialize members.
            SyntheticClassController(cls).synthesizeConstructor()

            return cls
        return functionWrapper
    
    def namingConventionDecorator(self, namingConvention):
        """
    :type namingConvention:INamingConvention
"""
        def decoratorFunction(cls):
            SyntheticClassController(cls).setNamingConvention(namingConvention)
            
            return cls
        return decoratorFunction

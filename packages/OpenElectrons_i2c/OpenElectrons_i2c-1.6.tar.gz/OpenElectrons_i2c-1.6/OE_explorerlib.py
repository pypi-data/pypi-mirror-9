#!/usr/bin/env python
#
# Copyright (c) 2014 OpenElectrons.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# History:
# Date      Author      Comments
# 04/15/14  Michael     Initial authoring
#

from OpenElectrons_i2c import OpenElectrons_i2c

class Explorer(OpenElectrons_i2c):  
    #"""Class for Explorer"""

    Explorer_ADDRESS = 0x00
    
    ## Initialize the class with an i2c address 
    #  @param self The object pointer.
    #  @param Explorer_address Address of your device.
    def __init__(self, explorer_address = Explorer_ADDRESS):
        #the Explorer address
        OpenElectrons_i2c.__init__(self, explorer_address >> 1) 
        
    ## Read an unsigned byte from your i2c device at a given location to check connection
    #  @param self The object pointer.
    #  @param reg The register to read from.
    def ping(self, reg):
        try:
            result = self.bus.read_byte_data(self.address, reg)
            return 1
        except:
            return -1
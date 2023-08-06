#
#
#                 SAMPLE 2 : EXPLAINS THE FUNCTION Arippe
#
#



# Example 1 

# First Import at most.
import Yrip

# Structure.
# Yrip -> Salt
#      -> __init__

#Salt -> <function @Yrip >

# Sample of using Y-RIP Hashing's Arippe.

Hashed = Yrip.Salt.Arippe("StrOftheTestTobeHashed") # The way is, String to be Byhashed or HaBitten
print Hashed
#>> Outputs a BIG ARRAY!

#Example 2

from Yrip import Salt
hashed = Salt.Arippe("StrOftheTestTobeHashed")
print hashed
#>> Same a BIG ARRAY

#Example 3

from Yrip.Salt import Arippe
Hash = Arippe("StrOftheTestTobeHashed")
print Hash
#>> BIG ARRAY

# Example with Class.

from Yrip import Salt
class Yrip_Example(Salt):
	def __init__ (self, a, b):
		self.Hash = a
		self.length = b
		self.Hashed = ''
	def doHash(self):
		self.Hashed	= self.Arippe(self.Hash, self.length)
		return self.Hashed

import sys

a = sys.argv[0]
print Yrip_Example(a)
# SAME BIG ARRAY!

# ~Dote.//Valid22//Flippr.
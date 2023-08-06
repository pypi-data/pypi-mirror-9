# Example 1

# First Import at most.
import Yrip

# Structure.
# Yrip -> Salt
#      -> __init__

#Salt -> <function @Yrip >

# Sample of using Y-RIP Hashing.

Hashed = Yrip.Salt.Yrip("StrOftheTestTobeHashed", 5) # The way is, String to be hashed ; The char length of hashed password you want.
pritn Hashed
#>> That will output :  cc39b
# If you want more Char increase the number( Argument 2).

# If the Given Argument (Char legth needed) is Greater than the Char generated.
# It will Make a number of checks.
# It will see which is greater, and, return char length of the difference of Both hash generated and given.
# If Subracted length is Greater than hashed salt, It will return either hash len - 789 or - 987.

#Example 2

from Yrip import Salt
hashed = Salt.Yrip("StrOftheTestTobeHashed", 9)
print hashed
#>> cc39b492d

#Example 3

from Yrip.Salt import Yrip
Hash = Yrip("StrOftheTestTobeHashed", 7)
print Hash
#>> cc39b49

# Example with Class.

from Yrip import Salt
class Yrip_Example(Salt):
	def __init__ (self, a, b):
		self.Hash = a
		self.length = b
		self.Hashed = ''
	def doHash(self):
		self.Hashed	= self.Yrip(self.Hash, self.length)
		return self.Hashed

import sys

a = sys.argv[0]
b = sys.argv[1]
print Yrip(a, b)
#>> len(HashedOf`a`) == b

# ~Dote.//Valid22//Flippr.
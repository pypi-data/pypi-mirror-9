import hashlib
import md5


def Yrip(passd, lent):

 	hash = md5.new(passd).hexdigest()[7:9]
   	hash += md5.new(passd).hexdigest()[0 : 23]
   	hash += md5.new(hash).hexdigest()[9:]
   	hash += hash + md5.new(md5.new(hash + md5.new(hash + passd).hexdigest()[7:9]).hexdigest()[7:9] + hash + md5.new(hash + passd).hexdigest()[7:9]).hexdigest()[7:9] + md5.new(hash + md5.new(hash + passd).hexdigest()[7:9]).hexdigest() + hash + md5.new(hash + passd).hexdigest()[7:9]
   	hash = hash[90 : 100] + hash[30:180] + hash[50:78]

   	mechanism = md5.new(hashlib.sha256(passd).hexdigest() + md5.new(passd + md5.new(hashlib.sha256(passd).hexdigest() + md5.new(passd).hexdigest() ).hexdigest() ).hexdigest()).hexdigest()
   	algorithm = (hash + (hash + mechanism + hashlib.sha256(hash + mechanism).hexdigest())) [:456]
   	hash += hashlib.sha256(mechanism).hexdigest()
   	algorithm = (hash + (hash + mechanism + hashlib.sha256(hash + mechanism).hexdigest())) [:456]
  	hash += algorithm + hashlib.sha256(hash[99:-34] + hash[0:99] + hash[100:]).hexdigest() + (hash[99:-34] + hash[0:99] + hash[100:]) + md5.new(hash[99:-34] + hash[0:99] + hash[100:]).hexdigest() 
  	hash += algorithm + (hash + md5.new(hash).hexdigest() + hashlib.sha256(hash).hexdigest()) + hashlib.sha256(md5.new(hash + md5.new(hash + hash).hexdigest()).hexdigest()).hexdigest() 
  	algorithm = (hash + (hash + mechanism + hashlib.sha256(hash + mechanism).hexdigest())) [:456]
  	mechanism = algorithm + (hash[:1000] + hash[0:100] + hash[101:400] + hash[800:900] + hash[900:1000])
  	
  	hash += algorithm + (mechanism + hash + md5.new(mechanism[:1000] + hash[:900] + hash[:455]).hexdigest())
  	
  	algorithm = (hash + (hash + mechanism + hashlib.sha256(hash + mechanism).hexdigest())) [:456]
  	hash += algorithm + (hash + algorithm)[:89]

  	if lent == 0 or lent < 0:
  		return hash

  	else:
  		if lent < len(hash) or lent == len(hash):
		  	return hash[:lent]
		else:
			if lent > len(hash):
				if lent-len(hash) < len(hash) or lent-len(hash) == len(hash):
					return hash[:lent-len(hash)]
				else:
					return hash[:len(hash)-789]	
			else:	
				if len(hash)-lent < len(hash) or len(hash)-lent == len(hash):
					return hash[:len(hash)-lent]
				else:
					return hash[:len(hash)-987]	

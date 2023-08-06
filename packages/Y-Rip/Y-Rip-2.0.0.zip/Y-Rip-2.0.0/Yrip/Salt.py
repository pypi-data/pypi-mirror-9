import hashlib, md5, string


def Trimlet(passd, lent):

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

def Arippe(abc):  
  c =  map(ord, (abc).encode('hex'))
  c += map(ord, abc)
  c += c +c
  c += sorted(c)
  c += map(ord, str(bytearray(c)))
  c += c
  c += str(bytearray(c)).encode('hex')  
  c +=  string.octdigits
  c +=  string.punctuation
  c +=  string.digits
  c +=  string.uppercase
  c +=  string.lowercase
  c +=  string.hexdigits
  c +=  string.zfill(8, 88)
  c +=  string.digits
  a  =  bytes(c).encode('hex')
  bc = len(a)
  if bc%2 == 0:
    b = a[:bc/2-900] + a[bc/2 - 900 : bc-100] 
    d = b[:len(b)/2] + b[len(b)/2 : len(b)-300]
    f = [d[:len(d)/2], d[len(d)/2 : ]]

    e = bytearray("/".join(f))
    g = []
    for k in e:
      g.append(k)
    return bytearray(g)
  else:
    a = str(a) + "K"  
    
    bc = len(a)
    if bc%2 == 0:
      b = a[:bc/2-900] + a[bc/2 - 900 : bc-100] 
      d = b[:len(b)/2] + b[len(b)/2 : len(b)-300]
      f = [d[:len(d)/2], d[len(d)/2 : ]]

      e = bytearray("/".join(f))
      g = []
      for k in e:
        g.append(k)
      return bytearray(g) 

def incode(sent,key):
    sent_l=list(sent)
    for i in range(0,len(sent_l)-1):
            uni=ord(sent_l[i])
            if(i%2==0):
                code=chr(round(10*(uni*key/(i+1)))) 
            else:                                                   #feel free to modify the equation!
                code=chr(round(10*(uni/key*(i+1))))
            sent_l[i]=code
    return "".join(sent_l)
def decode(sent,key):
    sent_l=list(sent)
    for i in range(0,len(sent_l)-1):
            uni=ord(sent_l[i])
            if(i%2==0):
                code=chr(round((uni*(i+1)/key)/10))
            else:                                                   #anyway, if you do modify, you'll need to
                code=chr(round((uni/(i+1)*key)/10))     #enter the reverse equation here.
            sent_l[i]=code
    return "".join(sent_l)

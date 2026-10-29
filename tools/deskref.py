import sys
A='0123456789ABCDEFGHJKMNPQRSTVWXYZ'
def fnv(t,seed):
    h=seed&0xffffffff
    for ch in t:
        h^=ord(ch); h=(h*0x01000193)&0xffffffff
    return h
def ref(s):
    t=s.strip(); a=fnv(t,0x811c9dc5); b=fnv(t,0x9e3779b9)
    bits=(a<<8)|(b&0xff); out=''
    for _ in range(8): out=A[bits&31]+out; bits>>=5
    return f'DR-{out[:4]}-{out[4:]}'
if __name__ == "__main__": print(ref(sys.argv[1]))

def syracuse(n):
    while n!=1:
        if n%2 == 0:
            n = n/2
            print n
        else:
            n = (n*3) + 1
            print n


def kartoffel():
    vari="kartoffel"
    while True:
        vari+="kartoffel"
        print vari
        

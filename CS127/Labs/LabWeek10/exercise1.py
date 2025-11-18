def calcXXX(a, b, c, d) :
    dict["XXX"] = a*b*c*d
    #return a*b*c*d
def calcXXA(a, b, c, d) :
    dict["XXA"] = a*b*c+d
    #return a*b*c+d
def calcXAX(a, b, c, d) :
    dict["XAX"] = a*b+c*d
    #return a*b+c*d
def calcAXX(a, b, c, d) :
    dict["AXX"] = a+b*c*d
    #return a+b*c*d
def calcAXA(a, b, c, d) :
    dict["AXA"] = a+b*c+d
    #return a+b*c+d
def calcAAA(a, b, c, d) :
    dict["AAA"] = a+b+c+d
    #return a+b+c+d
def calcXAA(a, b, c, d) :
    dict["XAA"] = a*b+c+d
    #return a*b+c+d
def calcAAX(a, b, c, d) :
    dict["AAX"] = a+b+c*d
    #return a+b+c*d
def calcAAS(a, b, c, d) :
    dict["AAS"] = a+b+c-d
    #return a+b+c-d
def calcSAA(a, b, c, d) :
    dict["SAA"] = a-b+c+d
    #return a-b+c-d
def calcASA(a, b, c, d) :
    dict["ASA"] = a+b-c+d
    #return a+b-c+d
def calcASS(a, b, c, d) :
    dict["ASS"] = a+b-c-d
    #return a+b-c-d
def calcSSS(a, b, c, d) :
    dict["SSS"] = a-b-c-d
    #return a-b-c-d
def calcSAS(a, b, c, d) :
    dict["SAS"] = a-b+c-d
    #return a-b+c-d
def calcSSA(a, b, c, d) :
    dict["SSA"] = a-b-c+d
    #return a-b-c+d
def calcSSX(a, b, c, d) :
    dict["SSX"] = a-b-c*d
    #return a-b-c*d
def calcSXS(a, b, c, d) :
    dict["SXS"] = a-b*c-d
    #return a-b*c-d
def calcXSS(a, b, c, d) :
    dict["XSS"] = a*b-c-d
    #return a*b-c-d
def calcXXS(a, b, c, d) :
    dict["XXS"] = a*b*c-d
    #return a*b*c-d
def calcSXX(a, b, c, d) :
    dict["SXX"] = a-b*c*d
    #return a-b*c*d
def calcXSX(a, b, c, d) :
    dict["XSX"] = a*b-c*d
    #return a*b-c*d
def calcSAX(a, b, c, d) :
    dict["SAX"] = a-b+c*d
    #return a-b+c*d
def calcSXA(a, b, c, d) :
    dict["SXA"] = a-b*c+d
    #return a-b*c+d
def calcXSA(a, b, c, d) :
    dict["XSA"] = a*b-c+d
    #return a*b-c+d
def calcXAS(a, b, c, d) :
    dict["XAS"] = a*b+c-d
    #return a*b+c-d
def calcASX(a, b, c, d) :
    dict["ASX"] = a+b-c*d
    #return a+b-c*d
def calcAXS(a, b, c, d) :
    dict["AXS"] = a+b*c-d
    #return a+b*c-d

dict = {}



def main() :
    a = int(input("Enter an integer for the A value: "))
    b = int(input("Enter an integer for the B value: "))
    c = int(input("Enter an integer for the C value: "))
    d = int(input("Enter an integer for the D value: "))
    calcXXX(a, b, c, d)
    calcXXA(a, b, c, d)
    calcXAX(a, b, c, d)
    calcAXX(a, b, c, d)
    calcAXA(a, b, c, d)
    calcAAA(a, b, c, d)
    calcXAA(a, b, c, d)
    calcAAX(a, b, c, d)
    calcAAS(a, b, c, d)
    calcSAA(a, b, c, d)
    calcASA(a, b, c, d)
    calcASS(a, b, c, d)
    calcSSS(a, b, c, d)
    calcSAS(a, b, c, d)
    calcSSA(a, b, c, d)
    calcSSX(a, b, c, d)
    calcSXS(a, b, c, d)
    calcXSS(a, b, c, d)
    calcXXS(a, b, c, d)
    calcSXX(a, b, c, d)
    calcXSX(a, b, c, d)
    calcSAX(a, b, c, d)
    calcSXA(a, b, c, d)
    calcXSA(a, b, c, d)
    calcXAS(a, b, c, d)
    calcASX(a, b, c, d)
    calcAXS(a, b, c, d)
    for key in dict.keys() :
        print(key, ":", dict[key])


main()


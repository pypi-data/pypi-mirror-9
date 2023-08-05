#!/usr/bin/env python3
from pyparsing import Literal, oneOf, Optional, OneOrMore, Word, ZeroOrMore, \
                      Empty, Combine

ALPHA = Literal("a") ^ Literal("b") ^ Literal("c") ^ Literal("d") ^ \
        Literal("e") ^ Literal("f") ^ Literal("g") ^ Literal("h") ^ \
        Literal("i") ^ Literal("j") ^ Literal("k") ^ Literal("l") ^ \
        Literal("m") ^ Literal("n") ^ Literal("o") ^ Literal("p") ^ \
        Literal("q") ^ Literal("r") ^ Literal("s") ^ Literal("t") ^ \
        Literal("u") ^ Literal("v") ^ Literal("w") ^ Literal("x") ^ \
        Literal("y") ^ Literal("z") ^ Literal("A") ^ Literal("B") ^ \
        Literal("C") ^ Literal("D") ^ Literal("E") ^ Literal("F") ^ \
        Literal("G") ^ Literal("H") ^ Literal("I") ^ Literal("J") ^ \
        Literal("K") ^ Literal("L") ^ Literal("M") ^ Literal("N") ^ \
        Literal("O") ^ Literal("P") ^ Literal("Q") ^ Literal("R") ^ \
        Literal("S") ^ Literal("T") ^ Literal("U") ^ Literal("V") ^ \
        Literal("W") ^ Literal("X") ^ Literal("Y") ^ Literal("Z")
#DIGIT = oneOf("0 1 2 3 4 5 6 7 8 9")
DIGIT = Literal("0") ^ Literal("1") ^ Literal("2") ^ Literal("3") ^ \
        Literal("4") ^ Literal("5") ^ Literal("6") ^ Literal("7") ^ \
        Literal("8") ^ Literal("9")
SAFE = Literal("$") ^ Literal("-") ^ Literal("_") ^ Literal("@") ^ \
       Literal(".") ^ Literal("&") ^ Literal("+") ^ Literal("-")
EXTRA = Literal("!") ^ Literal("*") ^ Literal("\"") ^ Literal("'") ^ \
        Literal("(") ^ Literal(")") ^ Literal(",")
RESERVED = Literal("=") ^ Literal(";") ^ Literal("/") ^ Literal("#") ^ \
           Literal("?") ^ Literal(":") ^ Literal(" ")
#HEX = Literal("a")
# HEX = oneOf("0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m n o p q r s t " +
#             "u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z")
HEX = DIGIT ^ Literal("a") ^ Literal("b") ^ Literal("c") ^ \
      Literal("d") ^ Literal("e") ^ Literal("f") ^ Literal("A") ^ \
      Literal("B") ^ Literal("C") ^ Literal("D") ^ Literal("E") ^ Literal("F")
NATIONAL = Literal("{") ^ Literal("}") ^ Literal("vline") ^ Literal("[") ^ \
           Literal("]") ^ Literal("\\") ^ Literal("^") ^ Literal("~")
PUNCTUATION = Literal("<") ^ Literal(">")
VOID = Empty()

escape = Literal('%') + HEX + HEX
digits = DIGIT + ZeroOrMore(DIGIT)
alphanum = ALPHA ^ DIGIT
alphanums = alphanum + ZeroOrMore(alphanum)

xalpha = ALPHA ^ DIGIT ^ SAFE ^ EXTRA ^ escape
xalphas = xalpha + ZeroOrMore(xalpha)
ialpha = ALPHA + ZeroOrMore(xalphas)

xpalpha = xalpha ^ Literal('+')
xpalphas = xpalpha + ZeroOrMore(xpalpha)

alphanum2 = ALPHA ^ DIGIT ^ Literal("-") ^ Literal("_") ^ \
            Literal(".") ^ Literal("+")

# gtype = xalpha
# fragmentid = xalphas
password = alphanum2 + ZeroOrMore(alphanum2)
user = alphanum2 + ZeroOrMore(alphanum2)
search = xalphas + ZeroOrMore(Literal("+") + xalphas)
segment = xpalphas
path = VOID ^ (segment + ZeroOrMore(Literal("/") + \
       (VOID ^ segment)))
# gcommand = path
port = digits
hostnumber = digits + Literal(".") + digits + Literal(".") + \
             digits + Literal(".") + digits
hostname = ialpha + ZeroOrMore(Literal(".") + ialpha)
# cellname = hostname
# FORMCODE = Literal("N") ^ Literal("T") ^ Literal("C")
# ftptype = (Literal("A") + FORMCODE) ^ (Literal("E") + FORMCODE) ^ \
#           (Literal("I")) ^ (Literal("L") + digits)
host = Combine(hostname) ^ Combine(hostnumber)
hostport = Combine(host + Optional(Literal(":") + port))
login = Optional(user + Optional(Literal(":") + password) + \
        Literal("@")) + hostport

httpaddress = Literal("http://") + hostport + \
              ZeroOrMore(Literal("/") + path) + \
              Optional(Literal("?") + search)
scheme = ialpha
url = httpaddress # Add more as needed
prefixedurl = Literal("url") + Literal(":") + url

def main():
    print(httpaddress.parseString("http://localhost/"))
    print(httpaddress.parseString("http://www.example.com/"))
    print(httpaddress.parseString("http://127.0.0.1/"))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from pyparsing import Combine, Group, Literal, oneOf, OneOrMore, Optional, \
                      Token, White, Word, ZeroOrMore, \
                      alphas, alphas8bit, alphanums, hexnums, nums, printables
from testbin.parser import parseurl

octet = [chr(i) for i in range(0,256)]
OCTET = oneOf(octet)
ctl = [chr(i) for i in range(0,32)]
ctl.append(chr(127))
CTL = oneOf(ctl)
CR = "\r"
LF = "\n"
CRLF = CR + LF
SP = ' '
HTAB = '\t'
WSP = Literal(HTAB) ^ Literal(SP)
WSP.leaveWhitespace()
LWS = Optional(ZeroOrMore(WSP) + CRLF) + OneOrMore(WSP)
LWS.leaveWhitespace()
SWS = Optional(LWS)
SWS.leaveWhitespace()

ICAP_Version = Literal("ICAP/1.0")
Token = Word(alphas)
Extension_Method = Token
Method = Literal("REQMOD") ^ Literal("RESPMOD") ^ Literal("OPTIONS") ^ \
         Extension_Method
Scheme = Literal("icap")
Host = parseurl.host
Port = parseurl.port
User_Info = parseurl.user + Optional(Literal(":") + parseurl.password)
Authority = Optional(User_Info + "@") + Host + Optional(":" + Port)
Abs_Path = parseurl.path
Net_Path = Combine(Authority) + Combine(Optional(Literal("/") + Abs_Path))
Query = parseurl.search
ICAP_URI = Combine(Scheme + Literal(":") + Literal("//")) + Net_Path + \
           Combine(Optional("?" + Query))
Request_Line = Method + SP + ICAP_URI + SP + ICAP_Version + CRLF
Request_Line.leaveWhitespace()
text = set(octet).difference(set(ctl))
TEXT = oneOf(list(text))
TEXT.leaveWhitespace()
Generic_Field_Content = ZeroOrMore(TEXT)
Generic_Field_Content.leaveWhitespace()
"""
<the OCTETs making up the field-value
                        and consisting of either *TEXT or
                        combinations of token, separators,
                        and quoted-string>
"""
Generic_Field_Value = Combine(Generic_Field_Content) ^ LWS
Generic_Field_Value.leaveWhitespace()
Extension_Field_Name  = Literal("X-") + Token
Extension_Field_Name.leaveWhitespace()
Common_Field_Name  = Literal("Cache-Control") ^ Literal("Connection") ^ \
                     Literal("Date") ^ Literal("Expires") ^ \
                     Literal("Pragma") ^ Literal("Trailer") ^ \
                     Literal("Upgrade") ^ Literal("Encapsulated") ^ \
                     Extension_Field_Name
Common_Field_Name.leaveWhitespace()
# REQUEST
Request_Field_Name = Literal("Authorization") ^ Literal("Allow") ^ \
                     Literal("From") ^ Literal("Host") ^ Literal("Referer") ^ \
                     Literal("User-Agent") ^ Literal("Preview")
Request_Field_Name.leaveWhitespace()
Request_Fields = Combine(Request_Field_Name) ^ Combine(Common_Field_Name)
Request_Fields.leaveWhitespace()
Request_Header = Combine(Request_Fields) + ":" + \
                 Combine(Optional(Generic_Field_Value))
Request_Header.leaveWhitespace()
Request_Body = ZeroOrMore(OCTET)
Request_Body.leaveWhitespace()
Request = Request_Line + ZeroOrMore(Request_Header + CRLF) + CRLF + \
          Combine(Optional(Request_Body))
Request.leaveWhitespace()
# RESPONSE
Extension_Code = Literal(nums) + Literal(nums) + Literal(nums)
Status_Code = Literal("100") ^ Literal("101") ^ Literal("200") ^ \
              Literal("201") ^ Literal("202") ^ Literal("203") ^ \
              Literal("204") ^ Literal("205") ^ Literal("206") ^ \
              Literal("300") ^ Literal("301") ^ Literal("302") ^ \
              Literal("303") ^ Literal("304") ^ Literal("305") ^ \
              Literal("306") ^ Literal("307") ^ Literal("400") ^ \
              Literal("401") ^ Literal("402") ^ Literal("403") ^ \
              Literal("404") ^ Literal("405") ^ Literal("406") ^ \
              Literal("407") ^ Literal("408") ^ Literal("409") ^ \
              Literal("410") ^ Literal("411") ^ Literal("412") ^ \
              Literal("413") ^ Literal("414") ^ Literal("415") ^ \
              Literal("416") ^ Literal("417") ^ Literal("500") ^ \
              Literal("501") ^ Literal("502") ^ Literal("503") ^ \
              Literal("504") ^ Literal("505") ^ Extension_Code
text_no_crlf = text.difference(set(CR)).difference(set(LF))
Reason_Phrase = ZeroOrMore(oneOf(list(text_no_crlf)))
Status_Line = ICAP_Version + SP + Status_Code + SP + Reason_Phrase + CRLF
Status_Line.leaveWhitespace()
Response_Field_Name = Literal("Server") ^ Literal("ISTag")
Response_Fields = Response_Field_Name ^ Common_Field_Name
Response_Header = Combine(Response_Fields) + ":" + \
                  Combine(Optional(Generic_Field_Value))
Response_Body = ZeroOrMore(OCTET)
Response = Status_Line + ZeroOrMore(Response_Header + CRLF) + CRLF + \
           Optional(Response_Body)
Response.leaveWhitespace()
# Message
ICAP_Message = Request ^ Response
ICAP_Message.leaveWhitespace()

def main():
    icap_with_req_body = "REQMOD icap://icap.example.com/mod ICAP/1.0\r\n" + \
                         "Authorization: ABC\r\nAllow: ABC\r\nFrom: ABC\r\n" + \
                         "Host: 1.1.1.1\r\nReferer: referer.example.com\r\n" + \
                         "User-Agent: Mozilla\r\nPreview: 0\r\n" + \
                         "Encapsulated: req-hdr=0, req-body=284\r\n\r\n" + \
                         "GET / HTTP/1.1\r\nHost: 127.0.0.1:80\r\n" + \
                         "User-Agent: Mozilla/5.0 (X11; Linux x86_64; " + \
                         "rv:30.0) Gecko/20100101 Firefox/30.0\r\n" + \
                         "Accept: text/html,application/xhtml+xml," + \
                         "application/xml;q=0.9,*/*;q=0.8\r\n" + \
                         "Accept-Language: en-US,en;q=0.5\r\n" + \
                         "Accept-Encoding: gzip, deflate\r\n" + \
                         "Connection: keep-alive\r\n\r\n"
    icap_no_req_body = "REQMOD icap://icap.example.com/mod ICAP/1.0\r\n" + \
                        "Authorization: ABC\r\nAllow: ABC\r\nFrom: ABC\r\n" + \
                        "Host: 1.1.1.1\r\nReferer: referer.example.com\r\n" + \
                        "User-Agent: Mozilla\r\nPreview: 0\r\n" + \
                        "Encapsulated: req-hdr=0, req-body=0\r\n\r\n"
    print(ICAP_Message.parseString(icap_with_req_body))
    print(ICAP_Message.parseString(icap_no_req_body))

if __name__ == '__main__':
    main()

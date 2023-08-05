__author__ = 'dave'
import visa
import ctypes  # An included library with Python install.
import time

def writefile(filename, mydata):
    myfile = filename
    try:
        with open(myfile,'w') as s:
            for item in mydata:
                s.write(item)                
    except IOError as err:
            print('File error: ' + str(err))  
    return 
    
def print_green(mystring):
    """
    prints formatted text
    """
    style = 0
    fg = 32
    bg = 48
    s1 = ''
    xformat = ';'.join([str(style), str(fg), str(bg)])
    s1 += '\x1b[%sm %s \x1b[0m' % (xformat, mystring)
    print s1

def Mbox(title, text):
    ctypes.windll.user32.MessageBoxA(0, text, title, 0x40 | 0x0)

def setstringq(str_in):
    #these are characters that are similar to single quote
    str_out = str_in.replace("\x91", "\'") 
    str_out = str_out.replace("\x92", "\'")
    str_out = str_out.strip()
    return str_out
    
def myprint(s, line):
    print line
    s.write(line + '\n')
    return
    
def myprintgreen(s, line):
    print_green(line)
    s.write(line + '\n')
    return
        
def setupTest(s,vna):
    myprintgreen(s,'Setup test')
    myprintgreen(s,vna.ask("OID"))
    writestr = ":SYST:ERR:CLE"
    vna.write(writestr)
    myprintgreen (s, 'Write: ' + writestr)
    myprintgreen(s,'# # #')
    return
    
def checkForErrors(s,vna):
    myprintgreen(s,'Check for Errors')
    myprintgreen(s,'Error Count: ' + vna.ask(":SYSTem:ERRor:COUNt?"))
    myprintgreen(s,'Errors: ' + vna.ask(":SYSTem:ERRor:NEXt?"))
    return   

def run(visa_id, filename):
    vna = visa.instrument(visa_id)
    vna.timeout = 60
    s = open(filename + '_out.txt','w')
    setupTest(s,vna)
    s2p = ''
    
    for line in open(filename):
        line = setstringq(line)
        if line.startswith(';') or line.startswith('//') or line.startswith('#'):
            line = line.split() #comment starts with #
        else:
            line = line.split(';') #wingpib commands
        if line:
            if line[0].startswith(';'):
                line[0] = line[0][1:]
                myprint( s,' //' + ' '.join(line))
            elif line[0].startswith('//'):
                line[0] = line[0][2:]
                myprint( s, ' //' + ' '.join(line))
            elif line[0].startswith('#'):
                line[0] = line[0][1:]
                myprint( s, ' //' + ' '.join(line))
            elif line[0].strip().upper() == 'E':
                qstr = ';'.join(line[1:])
                if qstr:
                    myprint( s, 'Query: ' + qstr)
                    #print line
                    response = vna.ask(qstr)
                else:
                    response = vna.read()
                if response.startswith('#9'):
                    myprint( s,  '\t' + response[0:50] + '...')
                else:    
                    myprint (s, '\t' + response)
            elif line[0].strip().upper() == 'R' or line[0].strip().upper() == 'F':
                qstr = ';'.join(line[1:])
                if qstr:
                    myprint( s, 'Query: ' + qstr)
                    #print line
                    response = vna.ask(qstr)
                else:
                    response = vna.read()
                if response.startswith('#9'):
                    myprint( s,  '\t' + response[0:50] + '...')
                    s2p = response[11:]
                else:    
                    myprint (s, '\t' + response)
            elif line[0].strip().upper() == 'WRITETOFILE':
                qstr = ';'.join(line[2:])
                if qstr:
                    myprint( s, 'Query: ' + qstr)
                    #print line
                    response = vna.ask(qstr)
                else:
                    response = vna.read()
                if response.startswith('#9'):
                    myprint( s,  '\t' + response[0:50] + '...')
                    writefile(line[1],response)
                else:    
                    myprint (s, '\t' + response)
                    writefile(line[1],response)
            elif line[0].strip().upper() == 'WRITETOFILENOARB':
                qstr = ';'.join(line[2:])
                if qstr:
                    myprint( s, 'Query: ' + qstr)
                    #print line
                    response = vna.ask(qstr)
                else:
                    response = vna.read()
                if response.startswith('#9'):
                    response = response[11:]
                    myprint( s,  '\t' + response[0:50] + '...')
                    writefile(line[1],response)
                else:    
                    myprint (s, '\t' + response)
            elif line[0].strip().upper() == 'READFROMFILE':
                myfile9 = open(line[1],'r')
                myfilestr=myfile9.read()
                myfile9.close()
                writestr = ';'.join(line[2:])
                myprint (s, 'Write: ' + writestr)
                if writestr.endswith(','):
                    myprint(s,'\t')
                else:
                    myfilestr = ' ' + myfilestr
                writestr += myfilestr
                vna.write(writestr)
            elif line[0].strip().upper() == 'O':
                writestr = ';'.join(line[1:])
                myprint (s, 'Write: ' + writestr)
                vna.write(writestr)
                #print line
            elif line[0].strip().upper() == 'PAUSE':
                myprint (s, 'PAUSE: ' + ''.join(line[1:]) )
                Mbox('PAUSE', ''.join(line[1:]))
            elif line[0].strip().upper().startswith('WAIT'):
                #line = line[0].split()
                mywait = int(line[1])
                time.sleep(mywait) # delays for 5 seconds
            elif line[0].strip().upper().startswith('TIME'):
                #line = line[0].split()
                myprint (s, 'Set TIMEOUT to ' + line[1])
                vna.timeout = int(line[1])
            elif line[0] == '':
                pass
            elif line[0].strip().upper() == 'IGNORE':
                myprint(s, 'Ignore the rest of the input file')
                break
            else:
                pass
    checkForErrors(s,vna)
    vna.write('RTL')
    return s2p

def print_time():
    print "From Print Time: ", time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    return

    
def writes3p(folder, filenameroot, mys2p, extrastring):
    myfile = folder + filenameroot + time.strftime("%d%b%Y_%H_%M_%S", time.localtime()) + '.s3p'
    mystring = mys2p.replace("\r\n", "\n")
    try:
        with open(myfile,'w') as s:
            s.write('! ' + extrastring + '\n')
            for item in mystring:
                s.write(item)                
    except IOError as err:
            print('File error: ' + str(err))  
    return 
    
def writeAnyType(folder, filenameroot, mys2p, extrastring, filetype):
    myfile = folder + filenameroot + time.strftime("%d%b%Y_%H_%M_%S", time.localtime()) + filetype
    mystring = mys2p.replace("\r\n", "\n")
    try:
        with open(myfile,'w') as s:
            s.write('! ' + extrastring + '\n')
            for item in mystring:
                s.write(item)                
    except IOError as err:
            print('File error: ' + str(err))  
    return   

def writejpg(folder, filenameroot, mys2p):
    myfile = folder + filenameroot + time.strftime("%d%b%Y_%H_%M_%S", time.localtime()) + '.jpg'
    try:
        with open(myfile,'wb') as s:
            for item in mys2p:
                s.write(item)                
    except IOError as err:
            print('File error: ' + str(err))  
    return





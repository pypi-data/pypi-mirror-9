__author__ = 'am100035'

import re

writers = ['ibwrt','ibwrta','viWrite','Write']
readers = ['ibrd','ibrda','viRead','Read','viScanf']
prelim = ['VISA','Formatted']

def stripCommand(L,ic,maxline):
    mycmd = []
    mylist = []
	
    while ic < maxline:
        line = L[ic].strip() 
        listcount = 0
        if line.startswith('00'):
            dave = line.split()
            for item in dave:
                if item.endswith(':'):
                    continue
                elif len(item) == 2:
                    try:
						if (listcount < 16):
							mylist.append(chr(int(item,16)))
							listcount = listcount + 1
                    except:
                        pass
                elif len(item) > 2 or len(item) < 2:
                    break
                else:
                    pass
                    
        elif re.findall(r"\A\d+\. ", line): #next command line
            break
            
        ic = ic + 1
              
    if mylist:
        mycmd = ''.join(mylist)
        if mycmd.startswith(':sens1:corr:coef'):
            mycmd = mycmd[0:25]
            mycmd = mycmd + ' ...\n'
        if mycmd.endswith("\n") == False:
            mycmd = mycmd + "\n"   
                          
    return mycmd


def findCommands(L):
    maxline = len(L)
    ic = 0
    commandList = []
    myWrites = []
    lastline = ''
    while ic < maxline:
        line = L[ic].strip()        
        d = re.findall(r"\A\d+\. ", line)
        if d:
            cmd = line.split("(")
            if cmd:
                command = cmd[0].split()
                if command[1] in writers:
                    print ' '.join(command)
                    mycmd = stripCommand(L,ic+1,maxline)
                    if mycmd != '\n':
                        commandList.append(mycmd)
                        myWrites.append('o; ' + mycmd)
                    lastline = ''                                                 
                elif command[1] in readers:
                    print ' '.join(command)
                    if lastline != 'e':
                        myWrites.append('e; \n')
                    lastline = 'e'
                elif command[1] in prelim:
                    if command[2] in writers:
                        print ' '.join(command)
                        mycmd = stripCommand(L,ic+1,maxline)
                        commandList.append(mycmd)
                        myWrites.append('o; ' + mycmd)
                        lastline = ''                                                
                    elif command[2] in readers:
                        print ' '.join(command)
                        if lastline != 'e':
                            myWrites.append('e; \n')
                        lastline = 'e'       
        ic = ic+1
    return myWrites,commandList

def readtrace(filename, script):
    try:
        with open(script,'w') as s, open(filename,'r') as iotrace:
            L = iotrace.readlines()
            myWrites, commandList = findCommands(L)    
            
            for item in myWrites:
                s.write(item)
                
    except IOError as err:
            print('File error: ' + str(err))
                   
    return commandList

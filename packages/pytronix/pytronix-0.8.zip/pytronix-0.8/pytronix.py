"""
PYTRONIX
a basic print server interface to scrape data from Tektronix oscilloscopes
concept and original version by Russell Anderson
rewritten with LPD server and binary transfer by Martijn Jasperse
"""
from telepythic.library import TekScope
import numpy as np
import time

def save_h5(dev,filename):
    import h5py
    # display a happy message
    dev.write('MESSage:STATE ON; SHOW "Downloading..."')
    # create the h5 file
    with h5py.File(filename,'w') as f:
        g = f.create_group('traces')
        # g.attrs['ip'] = dev.host
        g.attrs['id'] = dev.ask('*IDN?')
        print 'Querying channels'
        # check each channel
        for i in '1234':
            # is this channel displayed?
            if int(dev.ask('SELect:CH'+i+'?')):
                print '  Downloading channel',i
                wfmo, T, Y = dev.waveform(i)
                # put in the file
                d = g.create_dataset('CH'+i, data = np.transpose([T,Y]))
                for k in wfmo:
                    d.attrs[k] = wfmo[k]

def save_screenshot(ipaddr,filename):
    import urllib2, Image
    # get image of front-panel from the web server
    imgdata = urllib2.urlopen('http://' + ipaddr + '/image.png').read()
    # write to disk
    open(filename,'wb').write(imgdata)
    # open image
    img = Image.open(filename)
    # invert colors
    X = 255 - np.array(img)
    # replace brown with white
    X[X == (198,182,107)] = 255
    # save modified image to png
    Image.fromarray(X,'RGB').save(filename[:-4]+'_p.png','PNG')

    
def receive_ps(sock,filename):
    # world's dumbest print server (go read RFC1179)
    cmd = sock.recv(64)
    assert cmd[0] == '\x02', 'Expected incoming job'
    sock.send('\0') # ACK
    # receive control file (job information)
    # hypothetically the files could come in either order, but the tekscope uses this order
    cmd = sock.recv(64)
    assert cmd[0] == '\x02', 'Expected control file'
    msglen = int(cmd[1:cmd.find(' ')])
    sock.send('\0') # ACK
    ctrl = ''
    while len(ctrl) < msglen: ctrl += sock.recv(1024)
    sock.send('\0') # ACK
    # receive data file (actual postscript)
    cmd = sock.recv(64)
    assert cmd[0] == '\x03', 'Expected data file'
    msglen = int(cmd[1:cmd.find(' ')])
    sock.send('\0') # ACK
    data = ''
    while len(data) < msglen: data += sock.recv(102400)
    sock.send('\0') # ACK
    # save to file
    open(filename,'wb').write(data)
    return ctrl
    
    
def scrape(host, client=None):
    # label files by timestamp
    dest = time.strftime('%Y%m%dT%H%M%S')
    t0 = time.time()
    
    # receive the print request
    if client is not None:
        receive_ps(client,dest+'.ps')
        print 'Received postscript (in %.2fs)'%(time.time()-t0)
        client.close()
    
    print 'Attempting to scrape',host
    # now we know its ip, reconnect and scrape data
    dev = TekScope(host)
    # lock front panel
    dev.lock(True)
    # stop acquisition so data doesn't change while we download
    running = dev.ask('ACQ:STATE?')
    dev.write('ACQ:STATE STOP')
    try:
        t1 = time.time()
        save_screenshot(host,dest+'.png')
        print 'Took screenshot (in %.2fs)'%(time.time()-t1)
        
        t1 = time.time()
        save_h5(dev,dest+'.h5')
        print 'Downloaded data (in %.2fs)'%(time.time()-t1)
    except Exception as e:
        print 'ERROR >>', e
    # reset device
    dev.write('MESSage:CLEAR; STATE OFF')
    dev.write('ACQ:STATE '+running)
    dev.lock(False)
    dev.close()
    print '  Success (%.2fs elapsed)'%(time.time()-t0)

    
def serve(port=515):
    import socket, select 
    # create a socket and bind to port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(1.0)
    server.setblocking(True)
    server.bind(('', port))
    # listen for a connection
    server.listen(1)
    print '*** PYTRONIX SERVER ***'
    while 1:
        print 'Waiting for request...'
        # wait for a request
        while 1:
            # using select with timeout allows keyboard interrupt
            socklist = select.select([server],[server],[],0.5)
            if len(socklist[0]): break
        # accept a print request from the scope
        client, addr = server.accept()
        print '  Connection from',addr
        scrape(addr[0],client)
    server.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        scrape(sys.argv[1])
    else:
        serve()


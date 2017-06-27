import cv2
import socket
import numpy
import datetime
import sys
import os
import errno
import json


if __name__ == '__main__':
    if len(sys.argv)!=8:
        print 'Usage: python scriptname cameraname path/to/folder hostname port password display[on|off] rectify[on|off]'
        exit(-1)

    camera_name=sys.argv[1]
    path = sys.argv[2]
    hostname = sys.argv[3]
    port = int(sys.argv[4])
    password = sys.argv[5]
    display = sys.argv[6]
    rectify = sys.argv[7]

    print('camera name: ' + camera_name)
    print('path: ' + path)
    print('hostname:' + hostname)
    print('port:' + str(port))
    print ("Running")

    print type(hostname)
    print type(port)

    header_default = 'HTTP/1.1 200 OK\r\nServer: GoaHead\r\nTue, 12 Jun 2012 01:56:34 GMT\r\nContent-Type:image/jpeg\r\nContent-Length:9419\r\nConnection: close\n\n'
    header_delimiter = 'Connection: close\n\n'
    header_delimiter_len = len(header_delimiter)

    request = "GET /snapshot.cgi?user=admin&pwd=" + password + "&14885491932290.8336747860144513 HTTP/1.1\nHost: \nConnection: keep-alive\nAuthorization: Digest username=""admin"", realm=""GoAhead"", nonce=""311324594d6723ba1da492dd33285712"", uri=""/snapshot.cgi?user=admin&pwd=" + password + "&14885491932290.8336747860144513"", algorithm=MD5, response=""199aee099d86e2c9181d95e66c1a3f22"", opaque=""5ccc069c403ebaf9f0171e9517f40e41"", qop=auth, nc=0000004d, cnonce=""0bb1781ec73e8fcd""\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36\nAccept: image/webp,image/*,*/*;q=0.8\nReferer: http://nemesis17.homepc.it:2000/pda.htm\nAccept-Encoding: gzip, deflate, sdch\nAccept-Language: en-US,en;q=0.8\nCookie: noshow=0; browser=2\n\n"
    current_day = ''

    if display=='on': cv2.namedWindow(camera_name,cv2.WINDOW_NORMAL)
    if rectify == 'on':
        with open('C:/Users/alessandro/Desktop/simages/intrisics.txt') as data_file:
            data = json.load(data_file)
        mtx = data[0]
        dist = data[1]
        mtx = numpy.array(mtx)
        dist = numpy.array(dist)
        w=320
        h=180
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        print 'mtx'
        print mtx
        print 'dist'
        print dist
        print 'newcameramatrix'
        print newcameramtx
        cv2.namedWindow('rect' + camera_name, cv2.WINDOW_NORMAL)

    while 1:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((hostname , port))
            s.send(request)

            response=''
            while 1:
                data = s.recv(1000000)
                if len(data)==0:
                    break
                response=response+data

            pos_header_delimiter = response.find(header_delimiter)

            filename = str(datetime.datetime.now())
            filename = list(filename)
            for i in range(0,len(filename)):
                if filename[i]==':':
                    filename[i]='-'

            filename=''.join(filename)
            if current_day!=filename[0:10]:
                current_day=filename[0:10]
                try:
                    fullpath = path + '/' + camera_name + '/' + current_day
                    print fullpath
                    os.makedirs(fullpath)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        print exc
                        raise exc
                    pass

            responseb = numpy.fromstring(response[pos_header_delimiter+header_delimiter_len:], dtype=numpy.uint8)
            ofile = open(fullpath + '/' + filename + '.jpeg','wb')
            ofile.write(responseb)
            ofile.close()

            if (display == 'on') | (rectify=='on'):
                image = cv2.imdecode(responseb,cv2.IMREAD_COLOR)
                if rectify == 'on':
                    undistorted = cv2.undistort(image, mtx, dist, None, newcameramtx)
                    x, y, w, h = roi
                    undistorted = undistorted[y:y + h, x:x + w]
                    cv2.imshow('rect' + camera_name, undistorted)
                cv2.imshow(camera_name, image)
                key = cv2.waitKey(1)
                if key == ord('e'):
                    break

            s.close()
        except KeyboardInterrupt:
            print('Keyboard interrupt')
            exit(-1)
        except:
            key = cv2.waitKey(1)
            if key == ord('e'):
                break
            print 'exception: '
            print sys.exc_info()[0]
            continue

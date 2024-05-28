import requests
import time
import subprocess
from art import *
import os
#libraries needed: pip install art, pip install requests
#must have ffmpeg installed: use either homebrew for MacOs or follow https://ffmpeg.org/download.html for windows


####parameters####

prefix = 'wc'
spot = ['wc-lowers', 'wc-church', 'wc-oldmansanonofre', 'wc-tstreet', 'wc-malibufirstpt']
#get spot names like these from Surfline website, inspect cams page to find what they're called.
#spot = ['ec-narragansett', 'ec-secondbeachsurfers']
#prefix = 'ec'


Segments = 5
#Segments * 10 = length of vid in seconds

##################

cw = os.getcwd()
os.chdir(cw)
#ensures proper directory

fi = 1
while True:
    for i in range(len(spot)):
        it = 1
        try:
            os.chdir('{0}/{1}'.format(cw, spot[i]))
        except:
            os.mkdir('{0}/{1}'.format(cw, spot[i]))
            os.chdir('{0}/{1}'.format(cw, spot[i]))
        curcw = os.getcwd()
        while True:
            print('Iteration: {0}'.format(it))
            t0 = time.time()
            chunkfile = requests.get('https://cams.cdn-surfline.com/cdn-{0}/{1}/chunklist.m3u8'.format(prefix, spot[i]))
            #chunkfile contains details about the video files of the cams
            open('chunklist-{0}.txt'.format(spot[i]), 'wb').write(chunkfile.content)
            with open(r'chunklist-{0}.txt'.format(spot[i]), 'r') as chunkfile:
                #following code searches the file and saves certain parts to variahles
                contents = chunkfile.read()
                list_form = contents.split()
                seq_pos = contents.find('#EXT-X-MEDIA-SEQUENCE:')
                seq_line = 0
                for entry in list_form:
                    if 'MEDIA-SEQ' in entry:
                        break
                    seq_line += 1
                try:
                    seq_line_text = list_form[seq_line]
                except:
                    print('{0} failed to fetch'.format(spot[i]))
                    break
                seq_line_relative_pos = (len(seq_line_text))-((len(seq_line_text))-22)
                seq_line_relative_pos_delta_to_EOL = (len(seq_line_text))-22
                seq_absolute_pos = seq_pos + seq_line_relative_pos
                chunkfile.seek(seq_absolute_pos)
                seq = chunkfile.read(seq_line_relative_pos_delta_to_EOL)
                last_ts = contents.find('{0}.ts'.format(seq))
                last_ts_line = 0
                for entry in list_form:
                    if ('{0}.ts'.format(int(seq)+2)) in entry:
                        break
                    last_ts_line += 1
                last_ts_text = list_form[last_ts_line]
                ts = requests.get('https://cams.cdn-surfline.com/cdn-{0}/{1}/{2}'.format(prefix, spot[i], last_ts_text))
                #requests ts video file
                open('{0}{1}.ts'.format(spot[i], it), 'wb').write(ts.content)
                try:
                    with open("{0}.txt".format(spot[i]),'r') as f:
                        get_all=f.readlines()
                except:
                    open("{0}.txt".format(spot[i]),'w')
                    with open("{0}.txt".format(spot[i]),'r') as f:
                        get_all=f.readlines()
                    
                with open("{0}.txt".format(spot[i]),'w') as f:
                    for g,line in enumerate(get_all,1):      
                            f.writelines(line)
                    f.write("file '{0}/{1}{2}.ts'".format(curcw, spot[i], it) + '\n')
                it += 1
                if it > Segments:
                    #if ts files are all done being fetched, encode them to an mp4 file with ffmpeg
                    P = subprocess.Popen("ffmpeg -y -f concat -safe 0 -i {0}.txt -c copy {1}.mp4".format(spot[i], spot[i]), text=True, shell=True)
                    P.wait()
                    open("{0}.txt".format(spot[i]), "w").close()
                    if i+1 == len(spot):
                        tprint('Done  ( {0} / {1} )'.format(i+1, len(spot)))
                        print('{0} Done Fetching ({1}s), List finished'.format(spot[i], (it-1)*10))
                    else:
                        tprint('Done  ( {0} / {1} / {2})'.format(i+1, len(spot), fi))
                        print('{0} Done Fetching ({1}s), moving to {2}'.format(spot[i], (it-1)*10, spot[i+1]))
                    break
                t1 = time.time()
                delta = t1-t0
                time.sleep(10-delta)
    fi += 1
    time.sleep(600)

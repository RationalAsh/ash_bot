#!/usr/bin/python
import telegram
import time
import subprocess
from ash_bot_key import key

bot = telegram.Bot(token=key)
print bot.getMe()

def getCurrentVolume():
    vol_info = subprocess.check_output(['amixer', '-D', 'pulse', 'sget', 'Master'])
    idx = vol_info.find('%')
    vol = vol_info[idx-2:idx]
    return vol

def decideAction(message):
    text = message.lower().strip()
    reply = ''
    if text == 'play':
        subprocess.call(['rhythmbox-client', '--play'])
        reply = 'Now playing: '
        reply += subprocess.check_output(['rhythmbox-client', 
                                          '--print-playing'])
    elif text == 'pause' or text == 'stop':
        subprocess.call(['rhythmbox-client', '--pause'])
        reply = 'Paused'
    elif text == 'next':
        subprocess.call(['rhythmbox-client', '--next'])
        reply = 'Now playing: '
        reply += subprocess.check_output(['rhythmbox-client', 
                                          '--print-playing'])
    elif text == 'previous' or text =='back':
        subprocess.call(['rhythmbox-client', '--previous'])
        subprocess.call(['rhythmbox-client', '--previous'])
        reply = 'Now playing: '
        reply += subprocess.check_output(['rhythmbox-client', 
                                          '--print-playing'])
    elif text == 'louder' or text == 'volume up':
        reply = 'Volume Increased\n'
        subprocess.call(['amixer', 'sset', 'Master', '5%+'])
        reply += 'Volume is now at ' + getCurrentVolume()

    elif text == 'softer' or text == 'volume down':
        reply = 'Volume Decreased\n'
        subprocess.call(['amixer', 'sset', 'Master', '5%-'])
        reply += 'Volume is now at '+ getCurrentVolume()
        
    elif text == 'mute':
        reply = 'Muted'
        subprocess.call(['amixer', '-D', 'pulse', 'sset', 'Master', '1+', 'mute'])

    elif text == 'unmute':
        reply = 'Unmuted\n'
        subprocess.call(['amixer', '-D', 'pulse', 'sset', 'Master', '1+', 'unmute'])
        reply += 'Volume is now at ' + getCurrentVolume()

    elif text == 'shuffle':
        reply = 'Queue shuffled'
        subprocess.call(['rhythmbox-client', '--shuffle'])

    elif text == 'unshuffle':
        reply = 'Queue unshuffled'
        subprocess.call(['rhythmbox-client', '--no-shuffle'])

    elif ('what' in text) and ('playing' in text):
        reply = 'Now playing: '
        reply += subprocess.check_output(['rhythmbox-client', 
                                          '--print-playing'])
    return reply

def decideResponse(update):
    f_name = update.message.from_user.first_name
    text = update.message.text
    text_l = text.lower()
    reply = ''
    act_reply = decideAction(text_l)

    if ('hi' in text_l) or ('hello' in text_l) or \
       ('hey' in text_l):
        reply = 'Hi '+f_name+'!'
        reply += '\nI\'m ash_bot! I was designed by Ashwin. :)'
    elif 'mmmmmm' in text_l:
        reply = 'Nomnomnomnomnomnomnom'
    elif ('what' in text_l) and ('do' in text_l):
        reply = 'I can now control music on Ashwin\'s computer! :D\n'\
                'I can understand the commands:\n'\
                '1. Play\n2. Pause\n3. Next\n4. Previous\n'\
                '5. Louder or Volume Up\n6. Softer or Volume Down\n'\
                '7. Mute\n8. Unmute\n9. Shuffle\n10.Unshuffle\n'\
                'I can also tell you track is currently playing. Just'\
                ' ask me "What\'s playing?"'
    else:
        reply = text_l

    if act_reply and reply:
        reply += '\n\n----------------------\n'
        reply += act_reply
    else:
        reply += act_reply

    return reply

latest_id = 0

while True:
    latest_id = open('latest', 'r')
    offset = int(latest_id.readline().strip())
    latest_id.close()
    
    updates = bot.getUpdates(offset = offset + 1)
    if updates:
        for u in updates:
            reply = decideResponse(u)
            print reply
            try:
                print reply
                bot.sendMessage(chat_id=u.message.chat_id, text=reply)
            except:
                bot.sendMessage(chat_id=u.message.chat_id, text="I can still handle only text. :/")
                print reply

            uid = u.update_id
            if uid > offset:
                offset = uid
    else:
        print "No updates"

    print offset
    latest_id = open('latest', 'w')
    latest_id.write(str(offset))
    latest_id.close()
    time.sleep(1)

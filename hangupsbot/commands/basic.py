from hangups.ui.utils import get_conv_name
from hangupsbot.utils import text_to_segments
from hangupsbot.commands import command
import hangupsbot.commands
import hangupsbot
from sgDataApi.BusArrival import BusArrival
from sgDataApi.BusStop import BusStop
import subprocess
import sys
import nltk
import re
from textblob import TextBlob

### TODO ###
#1. integrate with Paho Mqtt
#2. subscribe to channel? #rpicenter 
#3. what are the command available in the rpicenter? we need to allow user to access this.
#4. how to send back chat when getting return from mqtt?
# multi word command?

def contain_number(word):    
    return any(i.isdigit() for i in word)

def get_word_with_number(text):
    for word in text.split():
        if contain_number(word) == True: return word
    return ''

def get_url(text):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return ''.join(urls)


@command.register_unknown
def unknown_command(bot, event, *args):
    """Unknown command handler"""
    yield from event.conv.send_message(
        text_to_segments("I'm confused")
    )

@command.register
def getsubtitle(bot, event, *args):
    cmd = "getsubtitle"
    print("Command: " + cmd)
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = process.communicate()[0]
    yield from event.conv.send_message(text_to_segments('Status: ' + str(out)))

@command.register
def download(bot, event, *args):
    cmd = "magic -dl " + get_url(' '.join(args))
    print("Command: " + cmd)
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    #process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    out = process.communicate()[0]
    yield from event.conv.send_message(text_to_segments('Status: ' + str(out)))

@command.register
def rpicenter(bot, event, *args):
    yield from event.conv.send_message(text_to_segments('pong...'))

@command.register
def test(bot, event, *args):
    cmd = 'echo "yuhuu..."'
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out = process.communicate()[0]
    yield from event.conv.send_message(text_to_segments('output: ' + str(out)))

@command.register(keyword=['transport','vehicle'])
def bus(bot, event, *args):
    busStopID = get_word_with_number(' '.join(args))
    if busStopID == '':  busStopID = "59419"
    out = BusArrival().result(busStopID)
    yield from event.conv.send_message(text_to_segments('BusStopID:' + str(busStopID) + ' ' + str(out)))

@command.register
def listen(bot, event, *args):
    sentence = ' '.join(args)
    #tokens = nltk.word_tokenize(sentence)
    #result = nltk.pos_tag(tokens)
    
    tokens = TextBlob(sentence)
    result = []
    
    for word, pos in tokens.tags:
        if pos == 'NN': result.append(word) #.lemmatize()

    yield from event.conv.send_message(text_to_segments(str(result)))

@command.register
def fortune(bot, event, *args):
    cmd = '/usr/games/fortune'
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE#, shell=True
    )
    out = process.communicate()[0]
    yield from event.conv.send_message(text_to_segments(str(out)))


@command.register
def rpicenter(bot, event, *args):
    sentence = ' '.join(args)

    __conv_name__ = get_conv_name(event.conv, truncate=True).lower()
    #print("Conv name: " + str(__conv_name__))

    #send MQTT msg to the rpicenter
    bot.mqtt.reply(requestID=str(__conv_name__),msg=str(sentence))
    
    status = "Request Sent to rpicenter: " + str(__conv_name__)
    yield from event.conv.send_message(text_to_segments(str(status)))


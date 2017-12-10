#!/usr/bin/env python3
import telnetlib
import time, datetime
import requests
import json
import os
import sys
from bitshares.witness import Witness
from bitshares.account import Account
from bitshares.asset import Asset
from bitshares import BitShares

# witness/delegate/producer account name to check
witness = "roelandp"
backupsigningkey = "BTS6XXXXXX"                 # FALL BACK Hot Swappable Backup Signing Key
witnessurl = "https://bitsharestalk.org/index.php/topic,24017.msg304832.html" # Your Witness Announcement url

telegram_token = ""	                            # Create your Telegram bot at @BotFather (https://telegram.me/botfather)
telegram_id    = ""                             # Get your telegram id at @MyTelegramID_bot (https://telegram.me/mytelegramid_bot)
walletpwd      = ""                             # Your UPTICK wallet unlock code

websocket		= "wss://node.bitshares.eu" #seednode to connect to!
seed_host               = "seed.roelandp.nl"    # hostname/ip for the public seed to monitor
seed_port               = 1776                  # port for the public seed to monitor (bitshares default = 1776)
seed_timeout_check      = int(10)               # seconds before timeout is called on telnet public seed operation.
check_rate              = int(45)               # amount of time (seconds) for the script to sleep before next check! Every x seconds the script will check missed blocks. 
check_rate_feeds_seed   = int(3600)             # set this to a considerably higher amount of seconds than check_rate so this script won't check your price_feed and seed availibility as much as that.
currentmisses           = int(0)                # current block misses (note this is set at -1 missed blocks so you will get 1 initial notification if you have more than 0 blocks missed currently. You could set this to your current count of misses to prevent the inital notification) 
startmisses             = int(-1)               # global holder of misses at start of script 
feeds_to_check          = ["USD","EUR","CNY"]   # feel free to add more pricefeeds here to monitor. If you have them all in one script you could consider limiting it to 1 of those in that pricefeed script. As long as the script runs at your given (cronjob) interval and you don't get notifications, you know at least the script is still running :P 
feed_warning_treshold   = int(10)               # hours of no pricefeed updates before you get a notification
loopcounter             = int(0)                # this is an internal reference i++ counter needed for correct functioning of the script
tresholdwitnessflip     = int(5)                # after how many blocks the witness should switch to different signing key

check_rate_feeds_seed_ratio = round(check_rate_feeds_seed/check_rate, 0)

# Setup node instance
bitshares = BitShares(websocket)

# Telegram barebones apicall 
def telegram(method, params=None):
    url = "https://api.telegram.org/bot"+telegram_token+"/"
    params = params
    r = requests.get(url+method, params = params).json()
    return r

# Telegram notifyer
def alert_witness(msg):
    # Send TELEGRAM NOTIFICATION
    payload = {"chat_id":telegram_id, "text":msg}
    m = telegram("sendMessage", payload)

# Check availability of Seednode:
def check_seednode():
  try:
    tn = telnetlib.Telnet(seed_host, seed_port,seed_timeout_check)
    print(tn.read_all())
  except Exception as e:
    tel_msg = "Your public seednode for bitshares is not responding!\n\nat *"+seed_host+"*.\n\n_"+str(e)+"_"
    alert_witness(tel_msg)

# Check pricefeeds 
def check_pricefeeds(): 
  producer = Account(witness,bitshares_instance=bitshares)
  for symbol in feeds_to_check: 
    asset = Asset(symbol, full=True, bitshares_instance=bitshares)
    feeds = asset.feeds
    for feed in feeds:
      if feed["witness"].witness == producer["id"]:
        timedelta = datetime.datetime.utcnow() - feed['date']
        diff = int(timedelta.seconds) / 3600
        print(str(diff)+" hours since last publish of "+symbol)
        if(diff >= feed_warning_treshold):
          alert_witness("Bitshares Pricefeed warning!\n\nIt has been more than "+str(diff)+" since you last published "+symbol)

# Check how many blocks a witness has missed
def check_witness():
    global currentmisses
    global startmisses
    status = Witness(witness ,bitshares_instance=bitshares)
    missed = status['total_missed']
    print(str(loopcounter)+ ": Missed blocks = " + str(missed))
    if startmisses == -1:
        startmisses = missed
    if missed > currentmisses:
    # Could create the witness_update transaction and broadcast new signing key here to switch from main to backup
    # For now this script only alerts on telegram...
        alert_witness("You are missing blocks! Your current misses count = "+str(missed)+", which was "+str(currentmisses))
        currentmisses = missed
        if (currentmisses - startmisses) == tresholdwitnessflip:
            # we have the amount of misses compared to our treshold.... lets flip witnesses to backup.
            bitshares.wallet.unlock(walletpwd)
            bitshares.update_witness(witness,url=witnessurl,key=backupsigningkey) 
            alert_witness("If all went well we now switched to backupsigningkey - check https://cryptofresh.com/user/roelandp")


# Main Loop
if __name__ == '__main__':
    while True:
        check_witness()
        sys.stdout.flush()
        loopcounter += 1
        if(loopcounter % check_rate_feeds_seed_ratio == 0): 
          check_seednode()
          check_pricefeeds()
        time.sleep(check_rate)

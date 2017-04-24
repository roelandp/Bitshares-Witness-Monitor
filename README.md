# Bitshares-Witness-Monitor
Monitor your missed blocks, pricefeeds &amp; public seednode availability and get notifications on Telegram

This python3 script provides the monitoring of 3 core witness tasks and reports via a telegram bot API call the following:

**1. Monitor missing blocks**
Whenever a new block is missed you will get a notification. This part of the script can (and will) be extended towards automated switching to the backup witness signing key once a threshold is passed. 

**2. Monitor the availability of your public seednode**
By utilising the telnet library the script tries to connect to the given seednode and will report on time-out or errors. 

**3. Monitor the publishing of a set of assets' pricefeed(s)**
By requesting the asset's feeds and checking against your witness name (configurable) the script keeps monitoring how long since you posted the given asset's feed. Whenever the configurable threshold in hours has passed and you have not yet published a new feed for the asset, you will get a notification. 

## Dependencies 
- [Python Bitshares by @xeroc](https://github.com/xeroc/python-bitshares/)
- A telegram bot token so you can receive notifications 

*If you have any remarks/feedback or questions, please let me know! If you find this script useful, feel free to support my witness activities by voting for me on Bitshares username: `roelandp`.*

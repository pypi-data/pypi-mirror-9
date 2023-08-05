Default API ID are read from the files:
    Linux: $HOME/.smssendrc
    Windows: %USERPROFILE%/.smssendrc

Example usage:

from pysmsru import SMSRU
smsru = SMSRU(
    api_id='youapiid' - or set in .smssendrc
    debug=True|None - Print debug messages
    sendername='sender name' - Sender name (optional)
    time=10 - Send time in UNIX TIME format (optional)
    translit=True|None|False - Convert message to translit
    http_timeout=10|None - Timeout for http connection (optional, default is 10)
)
smsru.send_one(phone_to='79121234567', message='Hello World!')
smsru.send_scope(phones_to=['79120123456', '79120012345'], message='Hello World!')

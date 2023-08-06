import stream

STREAM_APP_ID = '2034'
STREAM_KEY = 'q94efzsuqtk6'
STREAM_SECRET_KEY = '9rqkenchqen98usj7qazt7tcdssgg5yx4hsq3kuq9pvhnu4n43jd39dvvd7k47b5'
STREAM_LOCATION = 'ap-southeast'


client = stream.connect(api_key=STREAM_KEY, api_secret=STREAM_SECRET_KEY, location=STREAM_LOCATION, timeout=30)
feed = client.feed('user', '1')
print feed.get()

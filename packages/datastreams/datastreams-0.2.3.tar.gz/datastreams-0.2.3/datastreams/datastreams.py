import os
import datetime
from pymongo import MongoClient

# Enumerated Types
class DatabaseDocumentTypes:
    Stream, Entry = range(1, 3)

class DataStreamsClient(object):
    def __init__(self, database=None, collection=None):
        # Check if running locally on on Heroku and setup MongoDB accordingly
        if 'MONGOLAB_URI' in os.environ:
            client = MongoClient(os.environ['MONGOLAB_URI'])
        else:
            client = MongoClient('mongodb://localhost:27017/')

        if database:
            db = getattr(client, str(database))
        else:
            try:
                db = client.get_default_database()
            except:
                db = client.data_streams

        if collection:
            self.collection = getattr(db, str(collection))
        else:
            self.collection = db.data

    def get_data_stream(self, stream_key):
        result = self.collection.find_one({'type': DatabaseDocumentTypes.Stream, 'stream_key': stream_key}, {'_id': 0, 'type': 0})

        if result:
            if 'fields' in result:
                return DataStream(self.collection, result['stream_key'], fields=result['fields'])
            else:
                return DataStream(self.collection, result['stream_key'])
        else:
            # throw better error here
            return 'no data stream found'

    def add_data_stream(self, stream_key, fields=None):
        stream = dict()
        stream['type'] = DatabaseDocumentTypes.Stream
        stream['stream_key'] = str(stream_key)

        if fields:
            stream['fields'] = fields

        self.collection.insert(stream)
        return self.get_data_stream(stream_key)

class DataStream(object):
    def __init__(self, collection, stream_key, fields=None):
        self.collection = collection
        self.key = str(stream_key)
        self.fields = fields

    @property
    def entries(self):
        return list(self.collection.find(
            {'stream_key': self.key, 'type': DatabaseDocumentTypes.Entry},
            {'_id': 0, 'type': 0, 'stream_key': 0}
        ))
    
    def add_entry(self, data):
        entry = dict()
        entry['type'] = DatabaseDocumentTypes.Entry
        entry['stream_key'] = self.key
        entry['timestamp'] = datetime.datetime.now().isoformat()

        if data:
            entry['data'] = data

        return str(self.collection.insert(entry))
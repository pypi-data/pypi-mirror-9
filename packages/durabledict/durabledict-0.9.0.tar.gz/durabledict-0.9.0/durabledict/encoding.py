import pickle
import base64
from functools import wraps


try:
    import simplejson as json
except ImportError:
    import json


class EncoderError(ValueError):
    pass


class EncodingError(EncoderError):
    pass


class DecodingError(EncoderError):
    pass


class Encoder(object):
    encoding_exceptions = ()
    decoding_exceptions = ()

    @property
    def encoder(self):
        raise NotImplementedError()

    @property
    def decoder(self):
        raise NotImplementedError()

    def encode(self, *args, **kwargs):
        try:
            return self.encoder(*args, **kwargs)
        except self.encoding_exceptions as e:
            raise EncodingError(e)

    def decode(self, *args, **kwargs):
        try:
            return self.decoder(*args, **kwargs)
        except self.decoding_exceptions as e:
            raise EncodingError(e)


class NoOpEncoding(Encoder):
    encode = staticmethod(lambda d: d)
    decode = staticmethod(lambda d: d)


class PickleEncoding(Encoder):
    encoding_exceptions = (pickle.PicklingError, )
    decoding_exceptions = (pickle.UnpicklingError, )

    @staticmethod
    def encoder(data):
        pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        return base64.encodestring(pickled)


    @staticmethod
    def decoder(data):
        pickled = base64.decodestring(data)
        return pickle.loads(pickled)


class JSONEncoding(Encoder):
    encoding_exceptions = (ValueError, )
    decoding_exceptions = (ValueError, )

    encoder = json.dumps
    decoder = json.loads


DefaultEncoding = PickleEncoding

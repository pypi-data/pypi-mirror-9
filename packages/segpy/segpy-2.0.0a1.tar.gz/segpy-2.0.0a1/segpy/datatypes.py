DATA_SAMPLE_FORMAT = {1: 'ibm',
                      2: 'int32',
                      3: 'int16',
                      5: 'float32',
                      8: 'int8'}

# A mapping from SEG Y data types to format characters used by the struct module
CTYPES = {'int32':  'i',
          'uint32': 'I',
          'int16':  'h',
          'uint16': 'H',
          'int8': 'b',
          'uint8': 'B',
          'float32':  'f',
          'ibm': 'ibm'}


CTYPE_DESCRIPTION = {'ibm': 'IBM float',
                     'int32': '32 bit signed integer',
                     'uint32': '32 bit unsigned integer',
                     'int16': '16 bit signed integer',
                     'uint16': '16 bit unsigned integer',
                     'float32': 'IEEE float32',
                     'int8': '8 bit signed integer (byte)',
                     'uint8': '8 bit unsigned integer (byte)'}


SIZES = dict(i=4,
             I=4,
             h=2,
             H=2,
             b=1,
             B=1,
             f=4,
             ibm=4)


def size_in_bytes(ctype):
    return SIZES[ctype]

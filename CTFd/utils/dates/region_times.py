import os
import time
os.environ['TZ'] = 'EST'
'''
[<region>] = [ start_in_epoch, end_in_epoch ]
'''
pattern = '%Y-%m-%d %H:%M:%S'
def epoch(d):
  return time.mktime(time.strptime(d, pattern))

region_times = {
  'CSAW Europe': [
    epoch('2018-11-8 15:00:00'),
    epoch('2018-11-10 3:00:00'),
  ],
  'CSAW Israel': [
    epoch('2018-11-8 23:00:00'),
    epoch('2018-11-10 11:00:00'),
  ],
  'CSAW US-Canada': [
    epoch('2018-11-8 21:00:00'),
    epoch('2018-11-10 9:00:00'),
  ],
  'CSAW Mexico': [
    epoch('2018-11-8 21:00:00'),
    epoch('2018-11-10 9:00:00'),
  ],
  'CSAW India': [
    epoch('2018-11-8 21:00:00'),
    epoch('2018-11-10 9:00:00'),
  ],
  'CSAW MENA': [
    epoch('2018-11-8 21:00:00'),
    epoch('2018-11-10 9:00:00'),
  ],
}

region_hides = {
  'CSAW Europe': epoch('2018-11-10 1:00:00'),
  'CSAW Israel': epoch('2018-11-10 9:00:00'),
  'CSAW US-Canada': epoch('2018-11-10 7:00:00'),
  'CSAW Mexico': epoch('2018-11-10 7:00:00'),
  'CSAW India': epoch('2018-11-10 7:00:00'),
  'CSAW MENA': epoch('2018-11-10 7:00:00'),
}
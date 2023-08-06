from datetime import timedelta
import sys

sys.path.append('.')

NUM_QUERIES = 100
script_params_pairs = [('values', {'values': i}) for i in xrange(NUM_QUERIES)]

BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

CELERY_IMPORTS = ('tasks', )
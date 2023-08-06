from celery import group, Celery
from celery.utils.log import get_task_logger
from rexpro.connection import RexProConnectionPool
from rexpro._compat import print_
import os

logger = get_task_logger(__name__)

pool = RexProConnectionPool(os.getenv('TITAN_HOST', 'localhost'),
                            int(os.getenv('TITAN_REXPRO_PORT', 8184)),
                            'graph')

app = Celery('tasks')
app.config_from_object('celeryconfig')


@app.task(timeout=5, max_retries=1)
def rexpro_query(script, params):
    with pool.connection() as conn:
        logger.info('Performing Query with script: {}\n\t and params: {}'.format(script, params))
        results = conn.execute(script=script, params=params)
        logger.info("Got Results from Query (script={}, params={}): {}".format(script, params, results))
        assert results == params['data']
    return results


@app.task(timeout=10, max_retries=1)
def start_massive_queries(script_params_pairs):
    num_queries = len(script_params_pairs)
    g = group([rexpro_query.s(script, params) for script, params in script_params_pairs])
    results = g().join()
    lresults = len(results)
    print_("Got {} Results of {}:".format(lresults, num_queries))
    for i, result in enumerate(results):
        print_("{} - {}".format(i, result))
        logger.info("{} - {}".format(i, result))
    print_("Got {} of {} Results ({}%):".format(lresults, num_queries, (lresults/float(num_queries))*100.0))
    return results
if __name__ == '__main__':
    import tasks
    from rexpro._compat import print_, xrange
    print_("Queuing up tasks...")
    SLOW_NETWORK_QUERY = """def test_slow_query(sleep_time, value) {
    sleep sleep_time
    return value
    }

    return test_slow_query(sleep_length, data)
    """

    NUM_QUERIES = 10000
    SLEEP_TIME = 1
    script_params_pairs = [(SLOW_NETWORK_QUERY, {'sleep_length': SLEEP_TIME, 'data': i}) for i in xrange(NUM_QUERIES)]

    results = tasks.start_massive_queries(script_params_pairs)
    print_("Got Results:")
    print_(results)

else:
    print_("This must be executed manually")
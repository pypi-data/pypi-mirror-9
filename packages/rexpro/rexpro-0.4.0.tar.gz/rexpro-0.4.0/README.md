rexpro
======

rexpro-python is a RexPro socket interface for python, specifically designed for use with Titan
(http://thinkaurelius.github.io/titan/) via RexPro (https://github.com/tinkerpop/rexster/wiki/RexPro).
For those already familiar with Blueprints (https://github.com/tinkerpop/blueprints/wiki) there is is a simple example.


[![wercker status](https://app.wercker.com/status/6a2160385debe13745f2ff3eec734dac/m/master "wercker status")](https://app.wercker.com/project/bykey/6a2160385debe13745f2ff3eec734dac)


Documentation
=============

rexpro documentation can be found at http://rexpro-python.readthedocs.org/

Installation
============

``$ pip install rexpro``

Testing
=======

To get rexpro unit tests running you'll need a titan installation with rexster server configured with a test graph setup::

        <graph>
            <graph-name>graph</graph-name>
            <graph-type>com.thinkaurelius.titan.tinkerpop.rexster.TitanGraphConfiguration</graph-type>
            <!-- <graph-location>/tmp/titan</graph-location> -->
            <graph-read-only>false</graph-read-only>
            <properties>
                <storage.backend>cassandra</storage.backend>
                <storage.index.search.backend>elasticsearch</storage.index.search.backend>
                <storage.index.search.directory>../db/es</storage.index.search.directory>
                <storage.index.search.client-only>false</storage.index.search.client-only>
                <storage.index.search.local-mode>true</storage.index.search.local-mode>
            </properties>
            <extensions>
              <allows>
                <allow>tp:gremlin</allow>
              </allows>
            </extensions>
        </graph>
        <graph>
            <graph-name>emptygraph</graph-name>
            <graph-type>tinkergraph</graph-type>
            <graph-mock-tx>true</graph-mock-tx>
            <extensions>
                <allows>
                    <allow>tp:gremlin</allow>
                </allows>
            </extensions>
        </graph>
        <graph>
            <graph-name>tinkergraph</graph-name>
            <graph-type>tinkergraph</graph-type>
            <graph-location>data/graph-example-1</graph-location>
            <graph-storage>graphson</graph-storage>
            <extensions>
                <allows>
                    <allow>tp:gremlin</allow>
                </allows>
            </extensions>
        </graph>


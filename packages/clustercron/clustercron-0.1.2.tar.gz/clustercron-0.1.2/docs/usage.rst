=====
Usage
=====


clustercron help::

    $ clustercron --help
    usage: clustercron [-h] [-v] {elb} ...

    Cron job wrapper that ensures a script gets run from one node in the cluster.

    positional arguments:
      {elb}          Cluster type
        elb          Scope AWS Elastic Load Balance

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  Show verbose info (level DEBUG). (default: False)


clustercron ELB help::

    $ clustercron ELB --help
    usage: clustercron ELB [-h] command

    positional arguments:
      command     Cron job command

    optional arguments:
      -h, --help  show this help message and exit

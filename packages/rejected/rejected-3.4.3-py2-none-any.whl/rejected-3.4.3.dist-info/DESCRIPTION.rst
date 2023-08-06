All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the rejected project nor the names of its
   contributors may be used to endorse or promote products derived from this
   software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Description: Rejected
        ========
        
        Rejected is a AMQP consumer daemon and message processing framework. It allows
        for rapid development of message processing consumers by handling all of the
        core functionality of communicating with RabbitMQ and management of consumer
        processes.
        
        Rejected runs as a master process with multiple consumer configurations that are
        each run it an isolated process. It has the ability to collect statistical
        data from the consumer processes and report on it.
        
        |Version| |Downloads| |Status| |Coverage| |License|
        
        Features
        --------
        
        - Dynamic QoS
        - Automatic exception handling including connection management and consumer restarting
        - Smart consumer classes that can automatically decode and deserialize message bodies based upon message headers
        - Metrics logging and submission to statsd
        - Built-in profiling of consumer code
        
        Documentation
        -------------
        
        https://rejected.readthedocs.org
        
        Example Consumer
        ----------------
        .. code:: python
        
            from rejected import consumer
            import logging
        
            LOGGER = logging.getLogger(__name__)
        
        
            class Test(consumer.Consumer):
                def process(self, message):
                    LOGGER.debug('In Test.process: %s' % message.body)
        
        Example Configuration
        ---------------------
        .. code:: yaml
        
            %YAML 1.2
            ---
            Application:
              poll_interval: 10.0
              log_stats: True
              statsd:
                enabled: True
                host: localhost
                port: 8125
              Connections:
                rabbitmq:
                  host: localhost
                  port: 5672
                  user: guest
                  pass: guest
                  ssl: False
                  vhost: /
                  heartbeat_interval: 300
              Consumers:
                example:
                  consumer: rejected.example.Consumer
                  connections: [rabbitmq]
                  qty: 2
                  queue: generated_messages
                  dynamic_qos: True
                  ack: True
                  max_errors: 100
                  config:
                    foo: True
                    bar: baz
            
             Daemon:
               user: rejected
               group: daemon
               pidfile: /var/run/rejected/example.%(pid)s.pid
            
             Logging:
               version: 1
               formatters:
                 verbose:
                   format: "%(levelname) -10s %(asctime)s %(process)-6d %(processName) -15s %(name) -25s %(funcName) -20s: %(message)s"
                   datefmt: "%Y-%m-%d %H:%M:%S"
                 syslog:
                   format: "%(levelname)s <PID %(process)d:%(processName)s> %(name)s.%(funcName)s(): %(message)s"
               filters: []
               handlers:
                 console:
                   class: logging.StreamHandler
                   formatter: verbose
                   debug_only: true
                 syslog:
                   class: logging.handlers.SysLogHandler
                   facility: local6
                   address: /var/run/syslog
                   #address: /dev/log
                   formatter: syslog
               loggers:
                 my_consumer:
                   level: INFO
                   propagate: true
                   handlers: [console, syslog]
                 rejected:
                   level: INFO
                   propagate: true
                   handlers: [console, syslog]
                 urllib3:
                   level: ERROR
                   propagate: true
               disable_existing_loggers: false
               incremental: false
        
        
        Version History
        ---------------
        Available at https://rejected.readthedocs.org/en/latest/history.html
        
        .. |Version| image:: https://badge.fury.io/py/rejected.svg?
           :target: http://badge.fury.io/py/rejected
        
        .. |Status| image:: https://travis-ci.org/gmr/rejected.svg?branch=master
           :target: https://travis-ci.org/gmr/rejected
        
        .. |Coverage| image:: https://coveralls.io/repos/gmr/rejected/badge.png
           :target: https://coveralls.io/r/gmr/rejected
          
        .. |Downloads| image:: https://pypip.in/d/rejected/badge.svg?
           :target: https://pypi.python.org/pypi/rejected
           
        .. |License| image:: https://pypip.in/license/rejected/badge.svg?
           :target: https://rejected.readthedocs.org
        
Keywords: amqp rabbitmq
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: License :: OSI Approved :: BSD License

import sys
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    stream=sys.stdout
                    )
class logfilter(logging.Filter):
    def filter(self, record):
        return not record.msg.startswith('i')

logger=logging.getLogger()
flt= logfilter()
logger.addFilter(flt)
logging.info('info')
logging.info('sssinfo')
logging.info('xxxinfo')
logging.debug('debug')
logging.warning('Warning')
#print dir(logging)

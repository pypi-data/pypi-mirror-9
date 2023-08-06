from multiprocessing import TimeoutError,current_process,Queue
from swallow.settings import logger
import sys
import datetime, time

# Get documents from a queue, process them according to a function, and pushes it to a queue
# @param p_inqueue     In queue containing docs to process
# @param p_outqueue Out queue where processed docs are pushed
# @param p_process    function taking a doc as an input and returning a list of docs as a result
def get_and_parse(p_inqueue,p_outqueue,p_process,**kwargs):
    """
        Gets doc from an input queue, applies transformation according to p_process function,
        then pushes the so produced new doc into an output queue

        p_process must take a "doc" as a first parameter
    """

    current = current_process()
    total_get_time = 0
    total_proc_time = 0
    nb_items = 0
    while True:
        try:
            logger.debug("(%s) Size of queues. in : %i / ou : %i",current.name,p_inqueue.qsize(),p_outqueue.qsize())
            # if (p_inqueue.qsize() == 0):
            #     logger.warn("ATTENTION FILE VIDE !!!")
            start_time = time.time()
            
            try:
                in_doc = p_inqueue.get(False)
            except Exception:
                pass
            else:
                nb_items += 1

                total_get_time += time.time() - start_time

                # Manage poison pill
                if in_doc is None:
                    logger.info("(%s) => Parser has received 'poison pill' and is now ending ...",current.name)
                    p_inqueue.task_done()
                    break

                # Call the proc with the arg list (keeping the * means : unwrap the list when calling the function)
                start_time = time.time()

                out_doc = p_process(in_doc,**kwargs)

                total_proc_time += time.time() - start_time

                for doc in out_doc:
                    p_outqueue.put(doc)

                p_inqueue.task_done()

        except TimeoutError:
            logger.warn('Timeout exception while parsing with %s method',p_process)
        except KeyboardInterrupt:
            logger.info("user interruption")
            sys.exit(0)

    logger.info("average get time : %fs",total_get_time/nb_items)
    logger.info("average proc time : %fs",total_proc_time/nb_items)

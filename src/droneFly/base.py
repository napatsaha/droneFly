import abc
import logging
import threading


logger = logging.getLogger(__name__)


class BaseWorker(threading.Thread):
    """
    A worker class based on Threads that is made to be compatible with
    running concurrently in a Tello drone program.

    Requires a `stopper` (`threading.Event`) termination event to be passed during
    initiation, as well as frame per second (`fps`), so that a run session can always
    be terminated whenever the passed event is `.set()`.
    """

    stopper: threading.Event
    # logger: logging.Logger

    def __init__(self,
                 stopper: threading.Event,
                 fps: int = 20,
                 **kwargs):
        super().__init__(**kwargs)

        self.stopper = stopper
        self.fps = fps

    def start(self) -> None:
        logger.info("Started %s Thread" % self.getName())
        super().start()

    def run(self):
        while not self.stopper.is_set():
            self._run()

            self.stopper.wait(1/self.fps)

        self.close()

    def close(self):
        if not self.stopper.is_set():
            self.terminate()

        logger.info("Ended %s Thread" % self.getName())

    def terminate(self):
        logger.info("Terminating Event called from %s Thread" % self.getName())
        self.stopper.set()

    @abc.abstractmethod
    def _run(self):
        """
        User-defined method that will be run within the while loop inside self.run()

        To exit the loop, self.terminate() must be called; otherwise, the loop will
        run indefinitely until self.stopper is set.

        """
        pass

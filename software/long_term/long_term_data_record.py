import time
import logging
from logging.handlers import TimedRotatingFileHandler

from software.signal_display.scintillator_display.display.impl_a.data_manager import test as DataRecorder


def record(logger):
    data_recorder = DataRecorder(debug=False)
    
    while True:
        if not data_recorder.has_data():
            time.sleep(0.001)
            continue

        value = data_recorder.get_data_from_arduino()
        logger.info(f"{time.time()},{value}")

        lsb = value & 0xFFFFFF
        b1 = (lsb >> 16) & 0xFF
        b2 = (lsb >> 8) & 0xFF
        b3 = lsb & 0xFF

        logger.debug("receive trigger: SiPM status")
        logger.debug(f"    {b1:02x}          {b2:02x}          {b3:02x}")
        logger.debug(f"    {b1:08b}    {b2:08b}    {b3:08b}")


def main(logger):
    while True:
        try:
            logger.info("start recorder")
            record(logger)
        except Exception as e:
            logger.warning(f"restart recorder because {e}")
            ...


if __name__ == "__main__":
    handler = TimedRotatingFileHandler(
        "sc_data.log", when="midnight", interval=1, backupCount=0
    )

    logger = logging.getLogger("RECORDER")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    main(logger)

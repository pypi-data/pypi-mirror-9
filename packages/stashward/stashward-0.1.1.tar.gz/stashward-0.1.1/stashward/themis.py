import logging
from stashward import StashwardHandler

if __name__ == "__main__":
    root = logging.getLogger('')
    root.setLevel(logging.INFO)
    handler = StashwardHandler("logs.rc.pdx.edu", 5043, ca_certs="/etc/pki/tls/certs/PSUCA.crt")
    root.addHandler(handler)
    logging.info("Foo")
    try:
        raise ValueError("foo")
    except ValueError:
        logging.exception("Foobar!")

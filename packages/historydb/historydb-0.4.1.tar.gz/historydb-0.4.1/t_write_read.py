import elliptics
from elliptics.core import exceptions_policy


def create_session(io_flags=0, no_exceptions=False):
    log = elliptics.Logger("/dev/stdout", 1)
    cfg = elliptics.Config()
    cfg.config.wait_timeout = 5
    cfg.config.check_timeout = 60
    node = elliptics.Node(log, cfg)
    node.add_remote("127.0.0.1", 1025, 2)
    groups = [1]
    session = elliptics.Session(node)
    session.set_ioflags(io_flags)
    session.set_cflags(0)
    session.set_groups(groups)
    if no_exceptions:
        session.set_exceptions_policy(exceptions_policy.no_exceptions)
    return session


def do_read_write(io_flags):
    session = create_session(io_flags)
    key, data = "ioserv.json", "data"
    print "Writing using async Session.write_data()"
    try:
        result = session.write_data(key, data)
        entries = result.get()
        if len(entries):
            print "  FAILED, expected no entries, got", len(entries), entries
            for entry in entries:
                print "  size: %s, error: '%s'" % (entry.size, entry.error)
        else:
            print "  OK, write failed"
    except Exception as e:
        print "  OK, write failed", e

    #session = create_session(io_flags)
    print "Writing using Session.write_file()"
    try:
        session.write_file(key, __file__)
        print "  FAIL, write_file didn't raised exception"
    except Exception as e:
        print "  Ok, failed to session.write_file:", e


def main():
    # print "\n\nFlags: elliptics.io_flags.append | elliptics.io_flags.cache"
    # do_read_write(elliptics.io_flags.append | elliptics.io_flags.cache)
    # import time
    # time.sleep(15)
    print "\n\nFlags: elliptics.io_flags.append"
    do_read_write(elliptics.io_flags.append)
    print "\n\nFlags: 0"
    do_read_write(0)


main()

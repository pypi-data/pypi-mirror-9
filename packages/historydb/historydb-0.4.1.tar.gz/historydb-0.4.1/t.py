from historydb import Provider


def main():
    provider = Provider(["127.0.0.1:1025:2"], [1])
    spread = provider.create_session().routes.spread()
    for group, info in spread.items():
        print "Group", group
        for adddress, percent in info.items():
            print "  %s:%s:%s - %.3f%%" % (adddress.host, adddress.port, adddress.family, percent)

    user, data = "user", "data"
    time = 1111111
    print provider.add_log(user, data, time)
    print provider.data_from_results(provider.get_user_logs(user, time))


main()

from . import tasks

import celery

class Agent(celery.apps.worker.Worker):
    pass


def main():
    print "hello"


if __name__ == '__main__':
    main()

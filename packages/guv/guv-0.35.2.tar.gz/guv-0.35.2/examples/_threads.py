"""Condition variable example
"""
import guv

guv.monkey_patch()

from guv import gyield, spawn
import threading


def conditions():
    cv = threading.Condition()
    print(cv, hasattr(cv, 'green'))
    print(cv._lock)

    items = []

    def produce():
        print('start produce()')
        with cv:
            for i in range(10):
                items.append(i)
                print('yield from produce()')
                gyield()

            print('notify')
            cv.notify()
        print('done produce()')

    def consume():
        print('start consume()')
        with cv:
            while not len(items) == 10:
                print('wait ({}/{})'.format(len(items), 10))
                cv.wait()

            print('items: {}'.format(len(items)))
        print('done consume()')

    spawn(produce)
    spawn(consume)

    print('switch to hub')
    gyield(False)
    print('done test')


def main():
    conditions()


if __name__ == '__main__':
    main()

import time

from curtsies import Input

wait = 3

def main():
    with Input() as input_generator:
        while True:
            d = input_generator.send(wait)
            if d is None:
                print('no input for %s seconds' % wait)
            else:
                print(d)
            time.sleep(.5)

if __name__ == '__main__':
    main()

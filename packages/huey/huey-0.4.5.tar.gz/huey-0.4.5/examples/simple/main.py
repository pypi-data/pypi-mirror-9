from config import huey
from tasks import count_beans


if __name__ == '__main__':
    beans = raw_input('How many beans? ')
    count_beans(int(beans))
    print('Enqueued job to count %s beans' % beans)

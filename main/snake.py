#!/usr/bin/env python3
# Simple console Snake (cross-platform, stdlib only)
# Run: python snake.py

import sys, time, random, os
from collections import deque

WINDOWS = os.name == "nt"
if WINDOWS:
    import msvcrt
else:
    import termios, tty, select

def get_key_nonblocking():
    if WINDOWS:
        if not msvcrt.kbhit():
            return None
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            m = {b'H':'UP', b'P':'DOWN', b'K':'LEFT', b'M':'RIGHT'}
            return m.get(ch2.decode('latin1'))
        else:
            c = ch.decode('latin1').lower()
            return {'w':'UP','s':'DOWN','a':'LEFT','d':'RIGHT'}.get(c)
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if not dr:
            return None
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':
            dr, _, _ = select.select([sys.stdin], [], [], 0.0001)
            if dr:
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    dr, _, _ = select.select([sys.stdin], [], [], 0.0001)
                    if dr:
                        ch3 = sys.stdin.read(1)
                        mapping = {'A':'UP','B':'DOWN','D':'LEFT','C':'RIGHT'}
                        return mapping.get(ch3)
            return None
        else:
            c = ch1.lower()
            return {'w':'UP','s':'DOWN','a':'LEFT','d':'RIGHT'}.get(c)

def cls():
    sys.stdout.write('\x1b[2J\x1b[H')
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write('\x1b[?25l'); sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\x1b[?25h'); sys.stdout.flush()

WIDTH, HEIGHT = 30, 20
TICK = 0.2

def random_free_cell(snake):
    while True:
        p = (random.randint(1, WIDTH), random.randint(1, HEIGHT))
        if p not in snake:
            return p

def draw(snake, food, score):
    sys.stdout.write('\x1b[H')
    sys.stdout.write('#'*(WIDTH+2) + '\n')
    for y in range(1, HEIGHT+1):
        row = ['#']
        for x in range(1, WIDTH+1):
            if (x,y) == snake[0]:
                row.append('O')
            elif (x,y) in snake_set:
                row.append('o')
            elif (x,y) == food:
                row.append('*')
            else:
                row.append(' ')
        row.append('#\n')
        sys.stdout.write(''.join(row))
    sys.stdout.write('#'*(WIDTH+2) + '\n')
    sys.stdout.write(f'Score: {score}   Controls: arrows or WASD. Press Ctrl+C to quit.\n')
    sys.stdout.flush()

def main():
    old_settings = None
    if not WINDOWS:
        old_settings = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())

    try:
        random.seed()
        hide_cursor()
        cls()

        start = (WIDTH//2, HEIGHT//2)
        snake = deque([start, (start[0]-1, start[1]), (start[0]-2, start[1])])
        direction = 'RIGHT'
        score = 0
        food = random_free_cell(snake)
        global snake_set
        snake_set = set(snake)

        DIR = {'UP':(0,-1), 'DOWN':(0,1), 'LEFT':(-1,0), 'RIGHT':(1,0)}
        opposite = {'UP':'DOWN','DOWN':'UP','LEFT':'RIGHT','RIGHT':'LEFT'}

        draw(snake, food, score)

        while True:
            t0 = time.time()
            k = get_key_nonblocking()
            if k and k in DIR and k != opposite[direction]:
                direction = k

            dx, dy = DIR[direction]
            nx, ny = snake[0][0] + dx, snake[0][1] + dy

            if nx < 1 or nx > WIDTH or ny < 1 or ny > HEIGHT:
                break

            new_head = (nx, ny)
            if new_head in snake_set and new_head != snake[-1]:
                break

            snake.appendleft(new_head)
            snake_set.add(new_head)

            if new_head == food:
                score += 1
                food = random_free_cell(snake)
            else:
                tail = snake.pop()
                snake_set.discard(tail)

            draw(snake, food, score)

            # Победа при заполнении всего поля
            if len(snake) == WIDTH * HEIGHT:
                sys.stdout.write('\nПобеда! Ты заполнил всё поле!\n')
                sys.stdout.flush()
                time.sleep(1)
                break

            dt = time.time() - t0
            if dt < TICK:
                time.sleep(TICK - dt)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        if not WINDOWS and old_settings:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        sys.stdout.write('\nGame over. Final score: %d\n' % score)
        sys.stdout.flush()

if __name__ == "__main__":
    main()

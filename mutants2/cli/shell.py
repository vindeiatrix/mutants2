from ..engine import world, persistence, render
from ..engine.player import CLASSES


def class_menu(p):
    while True:
        print("Choose your class:")
        for i, name in enumerate(CLASSES, 1):
            print(f"{i}. {name}")
        choice = input('class> ').strip().lower()
        if choice == 'back':
            break
        if choice in {str(i) for i in range(1, len(CLASSES) + 1)}:
            p.clazz = CLASSES[int(choice) - 1]
            persistence.save(p)
        else:
            print("Choose 1-5 or 'back'.")


def main() -> None:
    w = world.World()
    p = persistence.load()
    class_menu(p)
    last_move = None
    while True:
        try:
            cmd = input('> ').strip().lower()
        except EOFError:
            break
        if cmd.startswith('loo'):
            render.render(p, w)
        elif cmd.startswith('nor'):
            if p.move('north', w):
                last_move = 'north'
        elif cmd.startswith('sou'):
            if p.move('south', w):
                last_move = 'south'
        elif cmd.startswith('eas'):
            if p.move('east', w):
                last_move = 'east'
        elif cmd.startswith('wes'):
            if p.move('west', w):
                last_move = 'west'
        elif cmd.startswith('las'):
            if last_move:
                p.move(last_move, w)
        elif cmd.startswith('tra'):
            parts = cmd.split()
            year = int(parts[1]) if len(parts) > 1 else None
            p.travel(w, year)
        elif cmd.startswith('cla'):
            class_menu(p)
        elif cmd.startswith('exi'):
            persistence.save(p)
            break
        else:
            print('Commands: look, north, south, east, west, last, travel, class, exit')
        persistence.save(p)

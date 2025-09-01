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


def main(*, dev_mode: bool = False) -> None:
    w = world.World()
    p = persistence.load()
    class_menu(p)
    last_move = None
    while True:
        try:
            cmd = input('> ').strip().lower()
        except EOFError:
            break
        if cmd.startswith('debug'):
            if not dev_mode:
                print('Debug commands are available only in dev mode.')
            else:
                parts = cmd.split()
                if len(parts) >= 2 and parts[1] == 'shadow' and len(parts) == 3:
                    direction = parts[2]
                    if direction in {'north', 'south', 'east', 'west'}:
                        p.senses.add_shadow(direction)
                        print('OK.')
                    else:
                        print('Invalid direction.')
                elif len(parts) >= 2 and parts[1] == 'footsteps' and len(parts) == 3:
                    try:
                        p.senses.set_footsteps(int(parts[2]))
                        print('OK.')
                    except ValueError:
                        print('footsteps distance must be 1..4')
                elif len(parts) >= 2 and parts[1] == 'clear':
                    p.senses.clear()
                    print('OK.')
                else:
                    print('Invalid debug command.')
            continue
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

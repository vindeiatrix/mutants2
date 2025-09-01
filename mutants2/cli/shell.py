from ..engine import world, persistence, render


def main() -> None:
    w = world.World()
    p = persistence.load()
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
        elif cmd.startswith('exi'):
            persistence.save(p)
            break
        else:
            print('Commands: look, north, south, east, west, last, travel, exit')
        persistence.save(p)

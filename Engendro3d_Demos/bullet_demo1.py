from _do_import import resolve_import

resolve_import()

from _BaseDemo import game, runDemo

if __name__ == '__main__':
    mainGame = game()
    runDemo(mainGame, 'Physics and light Demo')

"""
Mind.test
by Jakov Manjkas
aka. Knowledge
"""

if __name__ == '__main__':
    import Knowledge
    import Orientation
else:
    from . import Knowledge
    from . import Orientation
import pygame

def test_know():
    """
    This test Mind.Knowledge.Knowledge
    """
    save = Knowledge.Knowledge('test')
    save['Player'] = 'live'
    save['Position'] = 1
    save[5] = 12.44
    save[3.1] = [1, "aaa", [1, 2], 5]
    print(save)
    print(save["player"])
    save.add_data('Player', 'live')
    save.add_data('Position', 1)
    save.add_data(5, 12.44)
    save.add_data(3.1, [1, "aaa", [1, 2], 5])
    print(save)
    save.save_data()


def test_load():
    """
    This test Mind.Knowledge.load
    test_know must be runed first!
    """
    load = Knowledge.load('test')
    print(load)
    load[623] = 'a'
    load.save_data()
    load[11] = 22
    load.add_data(623, 'a')
    load.save_data()
    load.add_data(11, 22)
    load = Knowledge.load('test')
    print(load)


def test_map():
    """
    This test Mind.Orientation.MAP
    and other map objects.
    """
    Map = Orientation.MAP(1000, 1000)
    Earth = Orientation.point(111, 234, Map, 'Earth')
    Point = Orientation.point(234, 222, Map)
    Galaxy = Orientation.group_of_points(Map, 'Some galaxy', Orientation.point(224, 111, Map, 'Vulcan'), Orientation.point(456, 31, Map))
    Sector = Orientation.rect(200, 200, 100, 100, Map, 'Sector_x')
    print(Map)
    print(str(Earth), 'in', str(Sector), '=', Earth in Sector)
    print(str(Point), 'in', str(Sector), '=', Point in Sector)
    for p in Map.at(111, 234):
        print(str(p))
    Subsector = Orientation.rect(220, 240, 20, 20, Map)
    Something = Orientation.rect(280, 280, 50, 50, Map)
    print(str(Subsector), 'in', str(Sector), '=', Subsector in Sector)
    print(str(Something), 'in', str(Sector), '=', Something in Sector)


def test_tiled_map(file_name):
    """
    This test Mind.Orientation.tiled_map .
    """
    Map = Orientation.tiled_map(file_name)
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption('test, arrows for moving')
    Map.set_screen(screen)
    x, y = Map.set_camera_pos(0, 0)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    x, y = Map.set_camera_pos(x, y - 10)
                if event.key == pygame.K_RIGHT:
                    x, y = Map.set_camera_pos(x + 10, y)
                if event.key == pygame.K_DOWN:
                    x, y = Map.set_camera_pos(x, y + 10)
                if event.key == pygame.K_LEFT:
                    x, y = Map.set_camera_pos(x - 10, y)
        screen.fill((255, 255, 255))
        Map.blit()
        pygame.display.flip()
    pygame.quit()

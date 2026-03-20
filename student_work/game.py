


# Good Luck!# The goals for this phase include:
# - Pick out some icons for your game
# - Establish a starting position for each icon
# - Pick a size for your playing spaces
# - Print your playing space with starting position of each icon

# To make this work, you may have to type this into the terminal --> pip install curses
#IMPORTS
import curses
import random
import time
    
#Dictionary that holds all the data for the game, including the size of the board, the position of the player, cop, exit, and obstacles, as well as the icons used to represent each element on the board.
game_data = {
    'width': 4,
    'height': 4,
    'player': {"x": 0, "y": 0, "score": 0, "room": 0},
    'cop': {"x": 2, "y": 2},
    'exit': [
        {"x": 3, "y": 3, "escaped": False},
    ],
    'obstacles': [
        {"x": 1, "y": 2},
        {"x": 3, "y": 1}
    ],

    # ASCII icons
    'player_icon': "\U0001F61F",
    'cop_icon': "\U0001F46E",
    'obstacle': "\U0001F4E6",
    'exit_icon': "\U0001F6AA",
    'empty': "  "
}

#Draws the game board on the terminal using the curses library. It iterates through each cell of the board and checks if it contains the player, cop, obstacles, or exit, and prints the corresponding icon. It also displays the player's score, current room, and instructions for moving.
def draw_board(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)

    stdscr.clear()
    for y in range(game_data['height']):
        row = ""
        for x in range(game_data['width']):
            # Player
            if x == game_data['player']['x'] and y == game_data['player']['y']:
                row += game_data['player_icon']
            # Eagle
            elif x == game_data['cop']['x'] and y == game_data['cop']['y']:
                row += game_data['cop_icon']
            # Obstacles
            elif any(o['x'] == x and o['y'] == y for o in game_data['obstacles']):
                row += game_data['obstacle']
            # Collectibles
            elif any(c['x'] == x and c['y'] == y and not c['escaped'] for c in game_data['exit']):
                row += game_data['exit_icon']
            else:
                row += game_data['empty']
        stdscr.addstr(y, 0, row, curses.color_pair(1))

    stdscr.addstr(game_data['height'] + 1, 0,
                  f"Moves: {game_data['player']['score']}",
                  curses.color_pair(1))
    stdscr.addstr(game_data['height'] + 2, 0,
                  "Move with W/A/S/D, Q to quit",
                  curses.color_pair(1))
    stdscr.addstr(game_data['height'] + 3, 0,
                  f"Room: {game_data['player']['room']}",
                  curses.color_pair(1))
                  
    stdscr.refresh()
#On input from the user, this function attempts to move the player in the specified direction (W/A/S/D). It checks if the move is valid (not off the board and not into an obstacle) and updates the player's position and score accordingly. If the move is invalid, it simply returns without making any changes.
def move_player(key):
    x = game_data['player']['x']
    y = game_data['player']['y']

    new_x, new_y = x, y
    key = key.lower()

    if key == "w" and y > 0:
        new_y -= 1
    elif key == "s" and y < game_data['height'] - 1:
        new_y += 1
    elif key == "a" and x > 0:
        new_x -= 1
    elif key == "d" and x < game_data['width'] - 1:
        new_x += 1
    else:
        return  # Invalid key or move off board


    # Check for obstacles
    if any(o['x'] == new_x and o['y'] == new_y for o in game_data['obstacles']):
        return False

    # Update position and increment score
    game_data['player']['x'] = new_x
    game_data['player']['y'] = new_y
    game_data['player']['score'] += 1

    return True
#After the player moves, this function randomly shuffles the possible directions (up, down, left, right) and attempts to move the cop in one of those directions. It checks if the new position is within the bounds of the board and does not contain an obstacle before updating the cop's position.
def move_cop():
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)
    ex, ey = game_data['cop']['x'], game_data['cop']['y']

    for dx, dy in directions:
        new_x = ex + dx
        new_y = ey + dy
        if 0 <= new_x < game_data['width'] and 0 <= new_y < game_data['height']:
            if not any(o['x'] == new_x and o['y'] == new_y for o in game_data['obstacles']):
                game_data['cop']['x'] = new_x
                game_data['cop']['y'] = new_y
                break

#Generates obstacles based on map size, adding more obstacles as the map grows
def generate_obstacles():

    def is_valid_obstacle(x, y):
        # Don't place obstacles on the cop location, player location, or exit tile.
        if x == game_data['cop']['x'] and y == game_data['cop']['y']:
            return False
        if x == game_data['player']['x'] and y == game_data['player']['y']:
            return False
        if any(e['x'] == x and e['y'] == y for e in game_data['exit']):
            return False

        # Don't place obstacles adjacent to any exit (door area).
        for e in game_data['exit']:
            if abs(e['x'] - x) <= 1 and abs(e['y'] - y) <= 1:
                return False

        if any(o['x'] == x and o['y'] == y for o in game_data['obstacles']):
            return False
        return True

    num_obstacles = max(2, (game_data['width'] * game_data['height']) // 5)

    # Fill obstacle list up to the target count
    while len(game_data['obstacles']) < num_obstacles:
        x = random.randint(0, game_data['width'] - 1)
        y = random.randint(0, game_data['height'] - 1)
        if is_valid_obstacle(x, y):
            game_data['obstacles'].append({"x": x, "y": y})

    # Reposition all obstacles randomly (avoid cop / player / exit / around exit)
    for obstacle in game_data['obstacles']:
        while True:
            x = random.randint(0, game_data['width'] - 1)
            y = random.randint(0, game_data['height'] - 1)
            obstacle_set = [o for o in game_data['obstacles'] if o is not obstacle]

            if any(o['x'] == x and o['y'] == y for o in obstacle_set):
                continue
            if not is_valid_obstacle(x, y):
                continue

            obstacle['x'], obstacle['y'] = x, y
            break

#Runs the game
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    draw_board(stdscr)

    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key:
            if key.lower() == "q":
                break
            moved = move_player(key)

            if moved == True:
                move_cop()

            if (game_data['player']["x"] == game_data['cop']["x"] and
                    game_data['player']["y"] == game_data['cop']["y"]):
                    break

            if (game_data['player']["x"] == game_data['exit'][0]["x"] and
                    game_data['player']["y"] == game_data['exit'][0]["y"]):
                    game_data['player']["room"] += 1
                    game_data['player']["x"] = 0
                    game_data['player']["y"] = 0

                    game_data['cop']["x"] = 2
                    game_data['cop']["y"] = 2
                    
                    game_data['width'] += 1
                    game_data['height'] += 1
                    
                    game_data['exit'][0]["x"] = game_data['width'] - 1
                    game_data['exit'][0]["y"] = game_data['height'] - 1
                    
                    generate_obstacles()

            draw_board(stdscr)

        time.sleep(0.1)

    stdscr.clear()
    
    stdscr.addstr(2, 2, "GAME OVER")
    stdscr.addstr(3, 2, f"Final Score \n(Moves Survived): {game_data['player']['score']} \n(Rooms Passed): {game_data['player']['room']}")
    stdscr.refresh()
    time.sleep(5)


curses.wrapper(main)


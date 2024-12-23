import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window and box
window_width = 500
window_height = 500
box_width = 80
box_height = 40
# variables
shooter_x = window_width // 2
shooter_y = 50
projectiles = []  
falling_circles = []  
frame_count = 0
misfires = 0
score = 0
missed_falling_circles = 0  
paused = False
game_over = False
boxes = {
    'restart': {'x': window_width - 250, 'y': window_height - 50},
    'pause': {'x': window_width - 160, 'y': window_height - 50},
    'quit': {'x': window_width - 70, 'y': window_height - 50},
}

def write_pixel(x, y):
    glVertex2f(x, y)

# Midpoint Line Algorithm
def draw_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x, y = x1, y1
    write_pixel(x, y)

    while x < x2:
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1
        write_pixel(x, y)


# Midpoint Circle Algorithm
def draw_circle_midpoint(x_center, y_center, radius):
    x = 0
    y = radius
    d = 1 - radius
    draw_circle_symmetric_points(x_center, y_center, x, y)

    while x < y:
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
        draw_circle_symmetric_points(x_center, y_center, x, y)


def draw_circle_symmetric_points(x_center, y_center, x, y):
    write_pixel(x_center + x, y_center + y)
    write_pixel(x_center - x, y_center + y)
    write_pixel(x_center + x, y_center - y)
    write_pixel(x_center - x, y_center - y)
    write_pixel(x_center + y, y_center + x)
    write_pixel(x_center - y, y_center + x)
    write_pixel(x_center + y, y_center - x)
    write_pixel(x_center - y, y_center - x)

def draw_left_arrow(x, y, size):
    half_size = size // 2
    glBegin(GL_POINTS)

    # horizontal line
    for i in range(-half_size, half_size + 1):
        glVertex2f(x + i, y)

    left_corner_x = x - half_size

    #head
    for i in range(half_size):
        glVertex2f(left_corner_x+i, y + i + 1)
        glVertex2f(left_corner_x+i, y - i - 1)

    glEnd()





def draw_play_icon(x, y, size):
    half_size = size // 2
    glBegin(GL_POINTS)
    for i in range(-half_size, half_size + 1):
        for j in range(-i, i + 1):  
            glVertex2f(x + i, y + j)
    glEnd()


def draw_cross_icon(x, y, size):
    half_size = size // 2
    glBegin(GL_POINTS)
    for i in range(-half_size, half_size + 1):
        glVertex2f(x + i, y + i) 
        glVertex2f(x + i, y - i)  
    glEnd()




def draw_boxes():
    for box, pos in boxes.items():
        
        glColor3f(1.0, 1.0, 1.0) 
        glBegin(GL_POINTS)
        for x in range(pos['x'], pos['x'] + box_width + 1):
            glVertex2f(x, pos['y'])  
            glVertex2f(x, pos['y'] + box_height)  
        for y in range(pos['y'], pos['y'] + box_height + 1):
            glVertex2f(pos['x'], y)  
            glVertex2f(pos['x'] + box_width, y)  
        glEnd()

        # icon
        if box == 'restart':
            glColor3f(0.0, 1.0, 0.0)  
            draw_left_arrow(pos['x'] + box_width // 2, pos['y'] + box_height // 2, 20)
        elif box == 'pause':
            glColor3f(1.0, 1.0, 0.0)  
            draw_play_icon(pos['x'] + box_width // 2, pos['y'] + box_height // 2, 20)
        elif box == 'quit':
            glColor3f(1.0, 0.0, 0.0)  
            draw_cross_icon(pos['x'] + box_width // 2, pos['y'] + box_height // 2, 20)


def draw_shooter():
    glBegin(GL_POINTS)
    #line
    for y in range(0, 21):
        glVertex2f(shooter_x - 20, shooter_y + y)
        glVertex2f(shooter_x, shooter_y + y)
        glVertex2f(shooter_x + 20, shooter_y + y)
    #body
    for x in range(-15, 16):
        glVertex2f(shooter_x + x, shooter_y + 20)  
        glVertex2f(shooter_x + x, shooter_y + 50)  
    for y in range(20, 51):
        glVertex2f(shooter_x - 15, shooter_y + y)  
        glVertex2f(shooter_x + 15, shooter_y + y)  

    # top
    for i in range(-10, 11):
        glVertex2f(shooter_x + i, shooter_y + 50 + abs(i))  
    glEnd()


def spawn_falling_circle():
    global falling_circles
    new_circle = {
        'x': random.randint(50, window_width - 50),
        'y': window_height,
        'radius': 15,
        'dynamic': random.choice([True, False]),
        'expand': True,  
        'color': (random.random(), random.random(), random.random())  
    }
    falling_circles.append(new_circle)


def update():
    global projectiles, falling_circles, frame_count, misfires, score, missed_falling_circles, game_over

    if game_over or paused:
        return

    # projectiles
    for projectile in projectiles[:]:
        projectile['y'] += 3  
        if projectile['y'] > window_height:
            projectiles.remove(projectile)  

    # fc
    for circle in falling_circles[:]:
        circle['y'] -= 0.05  
        if circle['y'] < 0:  
            falling_circles.remove(circle)
            missed_falling_circles += 1  
            if missed_falling_circles >= 3: 
                game_over_screen()

       
        if circle['dynamic']:
            if circle['expand']:
                circle['radius'] += 0.05  
                if circle['radius'] >= 20: 
                    circle['expand'] = False  
            else:
                circle['radius'] -= 0.05  
                if circle['radius'] <= 5:  
                    circle['expand'] = True  

        # collision + projectiles
        for projectile in projectiles[:]:
            if abs(circle['x'] - projectile['x']) <= circle['radius'] and abs(circle['y'] - projectile['y']) <= circle['radius']:
                score += 2 if circle['dynamic'] else 1  # Bonus for dynamic circles
                print(f'Current Score: {score}')
                falling_circles.remove(circle)
                projectiles.remove(projectile)
                break  # Stop checking projectiles for this circle

        # collision + shooter 
        if circle['y'] <= shooter_y + 20 and abs(circle['x'] - shooter_x) <= circle['radius'] + 20:
            game_over_screen()

    frame_count += 1
    if frame_count >= 180 and len(falling_circles) < 3: 
        spawn_falling_circle()
        frame_count = 0 

    glutPostRedisplay()

# Function to handle keyboard input
def keyboard(key, x, y):
    global shooter_x, projectiles, paused, game_over

    if key == b'a' and shooter_x > 50:
        shooter_x -= 15  
    elif key == b'd' and shooter_x < window_width - 50:
        shooter_x += 15  
    elif key == b' ' and not game_over and not paused:  
        projectiles.append({'x': shooter_x, 'y': 70}) 


    glutPostRedisplay()

def mouse_click(button, state, x, y):
    global paused, game_over

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = window_height - y

        # Check which box was clicked
        for box, pos in boxes.items():
            if (pos['x'] <= x <= pos['x'] + box_width) and (pos['y'] <= y <= pos['y'] + box_height):
                if box == 'restart':  
                    restart_game()
                elif box == 'pause':  
                    paused = not paused
                elif box == 'quit': 
                    print(f"Goodbye! Final Score: {score}")
                    glutLeaveMainLoop()


def game_over_screen():
    global game_over
    game_over = True
    print(f"Game Over! Final Score: {score}")


def restart_game():
    global shooter_x, shooter_y, projectiles, falling_circles, frame_count, misfires, score, missed_falling_circles, game_over, paused
    shooter_x = window_width // 2
    projectiles = []
    falling_circles = []
    frame_count = 0
    misfires = 0
    score = 0
    missed_falling_circles = 0
    game_over = False
    paused = False
    print("Starting Over...")


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_boxes()

    draw_shooter()  

    # projectiles
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for projectile in projectiles:
        draw_circle_midpoint(projectile['x'], projectile['y'], 5)  # Projectile radius = 5
    glEnd()

    # falling circles
    for circle in falling_circles:
        glColor3f(*circle['color']) 
        glBegin(GL_POINTS)
        draw_circle_midpoint(circle['x'], circle['y'], int(circle['radius']))
        glEnd()



    glutSwapBuffers()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Set background color to black
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, window_width, 0.0, window_height)  # 2D orthogonal projection

# Main function
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Spaceship Shooter")

    init()
    glutDisplayFunc(display)    # Set display callback
    glutKeyboardFunc(keyboard)  # Set keyboard callback
    glutMouseFunc(mouse_click)
    glutIdleFunc(update)        # Set idle function for continuous updates

    glutMainLoop()

if __name__ == "__main__":
    main()

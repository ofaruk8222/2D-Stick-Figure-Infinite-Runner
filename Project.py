from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

WIDTH, HEIGHT = 800, 600
GROUND_Y = 100
PLAYER_X = 150

player_y = GROUND_Y
player_vy = 0
gravity = 0.8
jump_force = 15
is_jumping = False
game_over = False
score = 0
score_timer = 0
theta = 0

obstacles = []
obstacle_speed = 6
spawn_timer = 0
milestones = [300, 700, 1000, 1500, 2000]
milestone_idx = 0

def drawCircle(cx, cy, r):
    glBegin(GL_LINES)
    for i in range(360):
        angle1 = math.radians(i)
        angle2 = math.radians((i + 1) % 360)
        glVertex2f(cx + r * math.cos(angle1), cy + r * math.sin(angle1))
        glVertex2f(cx + r * math.cos(angle2), cy + r * math.sin(angle2))
    glEnd()

def drawCloud(cx, cy, r):
    glColor3f(1, 1, 1)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(36):
        angle = math.radians(i * 10)
        glVertex2f(cx + r * math.cos(angle), cy + r * math.sin(angle))
    glEnd()

def drawStickFigure():
    global theta
    glColor3f(0, 0, 0)
    glLineWidth(3)
    
    glBegin(GL_LINES)
    glVertex2f(PLAYER_X, player_y + 20)
    glVertex2f(PLAYER_X, player_y + 70)
    glEnd()
    
    drawCircle(PLAYER_X, player_y + 90, 20)
    
    glPointSize(4)
    glBegin(GL_POINTS)
    glVertex2f(PLAYER_X + 8, player_y + 95)
    glVertex2f(PLAYER_X + 18, player_y + 95)
    glEnd()
    glBegin(GL_LINE_STRIP)
    glVertex2f(PLAYER_X + 5, player_y + 88)
    glVertex2f(PLAYER_X + 13, player_y + 82)
    glVertex2f(PLAYER_X + 21, player_y + 88)
    glEnd()

    leg_angle = math.sin(theta) * 30
    arm_angle = math.sin(theta) * 40

    glPushMatrix()
    glTranslatef(PLAYER_X, player_y + 20, 0)
    
    glPushMatrix()
    glRotatef(leg_angle, 0, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(0, -40)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glRotatef(-leg_angle, 0, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(0, -40)
    glEnd()
    glPopMatrix()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(PLAYER_X, player_y + 60, 0)
    
    glPushMatrix()
    glRotatef(-arm_angle, 0, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(0, -30)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glRotatef(arm_angle, 0, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(0, -30)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def drawObstacles():
    glColor3f(1, 0, 0)
    for obs in obstacles:
        glBegin(GL_QUADS)
        glVertex2f(obs['x'], obs['y'])
        glVertex2f(obs['x'] + obs['w'], obs['y'])
        glVertex2f(obs['x'] + obs['w'], obs['y'] + obs['h'])
        glVertex2f(obs['x'], obs['y'] + obs['h'])
        glEnd()

def drawEnvironment():
    glColor3f(0.5, 0.8, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(0, GROUND_Y)
    glVertex2f(WIDTH, GROUND_Y)
    glVertex2f(WIDTH, HEIGHT)
    glVertex2f(0, HEIGHT)
    glEnd()

    drawCloud(200, 450, 30)
    drawCloud(240, 460, 40)
    drawCloud(280, 450, 30)
    drawCloud(600, 500, 35)
    drawCloud(640, 510, 45)

    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIDTH, 0)
    glVertex2f(WIDTH, GROUND_Y)
    glVertex2f(0, GROUND_Y)
    glEnd()
    
    glColor3f(0, 0, 0)
    glRasterPos2f(20, HEIGHT - 30)
    text = f"Score: {score}"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    if game_over:
        glColor3f(1, 0, 0)
        glRasterPos2f(WIDTH//2 - 100, HEIGHT//2)
        text = "GAME OVER - Press 'R'"
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def updatePhysics():
    global player_y, player_vy, is_jumping, game_over, score, theta, spawn_timer, obstacles
    global score_timer, milestone_idx, obstacle_speed
    
    if game_over:
        return

    player_vy -= gravity
    player_y += player_vy
    if player_y <= GROUND_Y:
        player_y = GROUND_Y
        player_vy = 0
        is_jumping = False

    if not is_jumping:
        theta += 0.2
    else:
        theta = 0

    spawn_timer += 1
    if spawn_timer > 90: 
        h = random.choice([30, 60, 90])
        obstacles.append({'x': WIDTH, 'y': GROUND_Y, 'w': 30, 'h': h})
        spawn_timer = 0

    for obs in obstacles:
        obs['x'] -= obstacle_speed

    obstacles = [obs for obs in obstacles if obs['x'] + obs['w'] > 0]

    player_box = {'x': PLAYER_X - 15, 'y': player_y, 'w': 30, 'h': 100}
    for obs in obstacles:
        if (player_box['x'] < obs['x'] + obs['w'] and
            player_box['x'] + player_box['w'] > obs['x'] and
            player_box['y'] < obs['y'] + obs['h'] and
            player_box['y'] + player_box['h'] > obs['y']):
            game_over = True

    score_timer += 1
    if score_timer >= 10:
        score += 1
        score_timer = 0
        
        if milestone_idx < len(milestones) and score >= milestones[milestone_idx]:
            obstacle_speed *= 1.15
            milestone_idx += 1

def update(val):
    updatePhysics()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    drawEnvironment()
    drawObstacles()
    drawStickFigure()
    glutSwapBuffers()

def keyboard(key, x, y):
    global player_vy, is_jumping, game_over, score, obstacles, player_y, score_timer, milestone_idx, obstacle_speed
    if key == b' ':
        if not is_jumping and not game_over:
            player_vy = jump_force
            is_jumping = True
    if key == b'r' or key == b'R':
        if game_over:
            game_over = False
            score = 0
            score_timer = 0
            milestone_idx = 0
            obstacle_speed = 6
            player_y = GROUND_Y
            player_vy = 0
            obstacles.clear()

def specialKeys(key, x, y):
    global player_vy, is_jumping
    if key == GLUT_KEY_UP:
        if not is_jumping and not game_over:
            player_vy = jump_force
            is_jumping = True

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WIDTH, HEIGHT)
glutCreateWindow("Stick Figure Runner")
glClearColor(1, 1, 1, 1)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WIDTH, 0, HEIGHT)
glutDisplayFunc(draw)
glutKeyboardFunc(keyboard)
glutSpecialFunc(specialKeys)
glutTimerFunc(0, update, 0)
glutMainLoop()
import pygame
import sys

# 初始化Pygame
pygame.init()

# 游戏配置
CELL_SIZE = 30
COLS = 20
ROWS = 15
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
FPS = 10

# 颜色定义 (黑白)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('吃豆人 - Pacman')
clock = pygame.time.Clock()

# 地图: 0=路径+豆子, 1=墙, 2=空路径(已吃)
# 关卡1 - 简单地图
level1_maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,1,0,1,0,0,0,1,1,0,0,0,1,0,1,0,0,1],
    [1,1,0,1,0,1,1,1,0,1,1,0,1,1,1,0,1,0,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# 关卡2 - 困难地图（更多墙壁，更窄的通道）
level2_maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,1,0,0,1],
    [1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# 当前关卡和地图
current_level = 1
maze = [row[:] for row in level1_maze]  # 深拷贝

# 吃豆人
pacman = {
    'x': 1,
    'y': 1,
    'direction': 'right',
    'mouth_open': True
}

# 分数
score = 0
level_start_score = 0  # 当前关卡开始时的分数
total_dots = sum(row.count(0) for row in maze)

def draw_maze():
    """绘制迷宫"""
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            if maze[row][col] == 1:  # 墙
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
            elif maze[row][col] == 0:  # 豆子
                dot_x = x + CELL_SIZE // 2
                dot_y = y + CELL_SIZE // 2
                pygame.draw.circle(screen, WHITE, (dot_x, dot_y), 3)

def draw_pacman():
    """绘制吃豆人"""
    center_x = pacman['x'] * CELL_SIZE + CELL_SIZE // 2
    center_y = pacman['y'] * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 3

    # 根据方向绘制吃豆人
    if pacman['mouth_open']:
        # 张嘴状态 - 用扇形表示
        if pacman['direction'] == 'right':
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)
            pygame.draw.polygon(screen, BLACK, [
                (center_x, center_y),
                (center_x + radius, center_y - radius//2),
                (center_x + radius, center_y + radius//2)
            ])
        elif pacman['direction'] == 'left':
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)
            pygame.draw.polygon(screen, BLACK, [
                (center_x, center_y),
                (center_x - radius, center_y - radius//2),
                (center_x - radius, center_y + radius//2)
            ])
        elif pacman['direction'] == 'up':
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)
            pygame.draw.polygon(screen, BLACK, [
                (center_x, center_y),
                (center_x - radius//2, center_y - radius),
                (center_x + radius//2, center_y - radius)
            ])
        elif pacman['direction'] == 'down':
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)
            pygame.draw.polygon(screen, BLACK, [
                (center_x, center_y),
                (center_x - radius//2, center_y + radius),
                (center_x + radius//2, center_y + radius)
            ])
    else:
        # 闭嘴状态 - 完整圆形
        pygame.draw.circle(screen, WHITE, (center_x, center_y), radius)

    # 切换嘴巴状态
    pacman['mouth_open'] = not pacman['mouth_open']

def move_pacman(dx, dy):
    """移动吃豆人"""
    global score

    new_x = pacman['x'] + dx
    new_y = pacman['y'] + dy

    # 检查是否可以移动
    if 0 <= new_y < ROWS and 0 <= new_x < COLS:
        if maze[new_y][new_x] != 1:  # 不是墙
            pacman['x'] = new_x
            pacman['y'] = new_y

            # 吃豆子
            if maze[new_y][new_x] == 0:
                maze[new_y][new_x] = 2
                score += 10

def draw_score():
    """显示分数和关卡"""
    font = pygame.font.Font(None, 36)
    level_score = score - level_start_score  # 当前关卡的分数
    text = font.render(f'Level: {current_level}  Score: {level_score}', True, WHITE)
    screen.blit(text, (10, HEIGHT - 40))

def draw_win():
    """显示胜利信息"""
    font = pygame.font.Font(None, 72)
    text = font.render('YOU WIN!', True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)

def draw_level_complete():
    """显示关卡完成信息"""
    font = pygame.font.Font(None, 60)
    text = font.render('LEVEL COMPLETE!', True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    screen.blit(text, text_rect)

    font_small = pygame.font.Font(None, 36)
    text2 = font_small.render('Press SPACE for next level', True, WHITE)
    text_rect2 = text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    screen.blit(text2, text_rect2)

def load_level(level):
    """加载指定关卡"""
    global maze, total_dots, current_level, pacman, level_start_score

    current_level = level
    level_start_score = score  # 记录当前关卡的起始分数

    if level == 1:
        maze = [row[:] for row in level1_maze]
    elif level == 2:
        maze = [row[:] for row in level2_maze]

    total_dots = sum(row.count(0) for row in maze)

    # 重置吃豆人位置
    pacman['x'] = 1
    pacman['y'] = 1
    pacman['direction'] = 'right'

# 游戏主循环
running = True
frame_count = 0
level_completed = False
game_won = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and level_completed:
                # 进入下一关
                if current_level < 2:
                    load_level(current_level + 1)
                    level_completed = False
            elif event.key == pygame.K_ESCAPE:
                running = False

    # 检测按键状态（长按才移动）
    if not level_completed and not game_won:
        keys = pygame.key.get_pressed()
        move_direction = None

        if keys[pygame.K_UP]:
            move_direction = ('up', 0, -1)
        elif keys[pygame.K_DOWN]:
            move_direction = ('down', 0, 1)
        elif keys[pygame.K_LEFT]:
            move_direction = ('left', -1, 0)
        elif keys[pygame.K_RIGHT]:
            move_direction = ('right', 1, 0)

        # 移动吃豆人（只有按住方向键时才移动）
        if move_direction:
            pacman['direction'] = move_direction[0]
            move_pacman(move_direction[1], move_direction[2])

    # 清屏
    screen.fill(BLACK)

    # 绘制游戏元素
    draw_maze()
    draw_pacman()
    draw_score()

    # 检查是否完成当前关卡（吃光所有豆子）
    level_score = score - level_start_score  # 当前关卡获得的分数
    if level_score >= total_dots * 10 and not level_completed and not game_won:
        if current_level < 2:
            level_completed = True  # 关卡完成，等待进入下一关
        else:
            game_won = True  # 所有关卡完成，游戏胜利

    # 显示关卡完成或游戏胜利信息
    if level_completed:
        draw_level_complete()
    elif game_won:
        draw_win()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
import pygame
import sys

# 初始化pygame
pygame.init()

# 游戏窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("简易超级马里奥")

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (80, 80, 255)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 游戏参数
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 1
SCROLL_THRESH = 200

# 玩家类
class Mario(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumping = False
        self.direction = 0  # 0: 站立, 1: 右, -1: 左
        
    def update(self, platforms):
        # 重置水平移动
        dx = 0
        dy = 0
        
        # 获取按键输入
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -5
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx = 5
            self.direction = 1
        if key[pygame.K_SPACE] and not self.jumping:
            self.vel_y = -15
            self.jumping = True
        
        # 应用重力
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        # 检查与平台的碰撞
        for platform in platforms:
            # 水平碰撞
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # 垂直碰撞
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # 检查是否在平台上着陆
                if self.vel_y > 0:
                    self.vel_y = 0
                    dy = platform.rect.top - self.rect.bottom
                    self.jumping = False
                # 检查是否撞到平台底部
                elif self.vel_y < 0:
                    self.vel_y = 0
                    dy = platform.rect.bottom - self.rect.top
        
        # 更新位置
        self.rect.x += dx
        self.rect.y += dy
        
        # 确保玩家不会离开屏幕
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        return dx

# 平台类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        
    def update(self, scroll):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter = 0
        
        # 应用滚动
        self.rect.x -= scroll

# 创建精灵组
player_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# 创建玩家
mario = Mario(100, SCREEN_HEIGHT - 130)
player_group.add(mario)

# 创建地面
ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
platform_group.add(ground)

# 创建一些平台
platforms = [
    (100, 400, 100, 20),
    (300, 300, 100, 20),
    (500, 400, 100, 20),
    (700, 300, 100, 20)
]

for plat in platforms:
    p = Platform(plat[0], plat[1], plat[2], plat[3])
    platform_group.add(p)

# 创建敌人
enemy = Enemy(400, SCREEN_HEIGHT - 80)
enemy_group.add(enemy)

# 游戏循环
scroll = 0
bg_scroll = 0
running = True

while running:
    clock.tick(FPS)
    
    # 绘制背景
    screen.fill(BLUE)
    pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    
    # 更新玩家
    dx = mario.update(platform_group)
    
    # 计算滚动
    if mario.rect.right > SCREEN_WIDTH - SCROLL_THRESH and dx > 0:
        scroll = dx
        mario.rect.right = SCREEN_WIDTH - SCROLL_THRESH
    elif mario.rect.left < SCROLL_THRESH and dx < 0:
        scroll = dx
        mario.rect.left = SCROLL_THRESH
    else:
        scroll = 0
    
    # 更新背景滚动
    bg_scroll -= scroll
    
    # 更新平台和敌人位置
    for platform in platform_group:
        platform.rect.x -= scroll
    
    enemy_group.update(scroll)
    
    # 绘制精灵
    platform_group.draw(screen)
    player_group.draw(screen)
    enemy_group.draw(screen)
    
    # 检测与敌人的碰撞
    if pygame.sprite.spritecollide(mario, enemy_group, False):
        # 简单处理：如果马里奥从上方踩到敌人，消灭敌人
        for enemy in pygame.sprite.spritecollide(mario, enemy_group, False):
            if mario.vel_y > 0 and mario.rect.bottom < enemy.rect.centery:
                enemy.kill()
                mario.vel_y = -10  # 反弹
            else:
                # 游戏结束
                print("游戏结束!")
                running = False
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.update()

pygame.quit()
sys.exit()
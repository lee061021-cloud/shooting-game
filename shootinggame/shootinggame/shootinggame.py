import tkinter as tk
import random
import math



WIDTH, HEIGHT = 600, 800
PLAYER_W, PLAYER_H = 40, 20
BULLET_W, BULLET_H = 5, 10
ENEMY_W, ENEMY_H = 30, 20
NUM_STARS = 100
BOSS_W, BOSS_H = 120, 40
PLAYER_SPEED = 6



opening_flag = True

root = tk.Tk()
root.title("Shooting Game - Boss Stage 3")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()


stars = []
for _ in range(NUM_STARS):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    star = canvas.create_oval(x, y, x+size, y+size, fill="white", outline="")
    stars.append((star, size))

def update_stars():
    for star, size in stars:
        canvas.move(star, 0, size//2)
        x1, y1, x2, y2 = canvas.coords(star)
        if y1 > HEIGHT:
            canvas.move(star, 0, -HEIGHT-2)
    if not opening_flag:
        root.after(50, update_stars)

update_stars()


player = canvas.create_rectangle(
    WIDTH//2 - PLAYER_W//2,
    HEIGHT - 40,
    WIDTH//2 + PLAYER_W//2,
    HEIGHT - 20,
    fill="blue"
)

vx, vy = 0, 0
bullets = []
enemies = []
enemy_bullets = []
boss = None
boss_health = 0
boss_bar = None

score = 0
lives = 3
difficulty = 1
stage = 1
stage_score = 50
game_over_flag = False
boss_attack_cooldown = 0

score_text = canvas.create_text(10, 10, anchor="nw", fill="white", text=f"Score: {score}", font=("Arial", 16))
lives_text = canvas.create_text(10, 30, anchor="nw", fill="white", text=f"Lives: {lives}", font=("Arial", 16))
stage_text = canvas.create_text(10, 50, anchor="nw", fill="white", text=f"Stage: {stage}", font=("Arial", 16))
stage_message = None



def show_stage_message(stage_num):
    global stage_message
    if stage_message:
        canvas.delete(stage_message)
    stage_message = canvas.create_text(
        WIDTH//2, HEIGHT//2,
        text=f"Stage {stage_num}",
        font=("Arial", 30, "bold"),
        fill="yellow"
    )
    canvas.after(1000, lambda: canvas.delete(stage_message))



def key_down(e):
    global vx, vy
    if e.keysym == "Left":
        vx = -PLAYER_SPEED
    elif e.keysym == "Right":
        vx = PLAYER_SPEED
    elif e.keysym == "Up":
        vy = -PLAYER_SPEED
    elif e.keysym == "Down":
        vy = PLAYER_SPEED
    elif e.keysym == "space":
        shoot()

def key_up(e):
    global vx, vy
    if e.keysym in ("Left", "Right"):
        vx = 0
    if e.keysym in ("Up", "Down"):
        vy = 0

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)



def shoot():
    x1, y1, x2, y2 = canvas.coords(player)
    bullet = canvas.create_rectangle(
        (x1+x2)//2 - 2, y1 - 10, (x1+x2)//2 + 2, y1, fill="yellow"
    )
    bullets.append(bullet)

def spawn_enemy_bullet(x, y, target_x, target_y, speed=5):
    dx = target_x - x
    dy = target_y - y
    dist = math.hypot(dx, dy)
    vx_b = dx / dist * speed
    vy_b = dy / dist * speed
    bullet = {'id': canvas.create_rectangle(x-2, y, x+2, y+10, fill="orange"),
              'vx': vx_b, 'vy': vy_b}
    enemy_bullets.append(bullet)



def spawn_enemy():
    if stage >= 3:
        return
    x = random.randint(20, WIDTH-20)
    color = "red" if stage < 2 else "orange"
    enemy = canvas.create_rectangle(x, 0, x+ENEMY_W, ENEMY_H, fill=color)
    enemies.append(enemy)



def spawn_boss():
    global boss, boss_health, boss_attack_cooldown, boss_bar
    boss_health = 30
    boss = canvas.create_rectangle(WIDTH//2-BOSS_W//2, 50, WIDTH//2+BOSS_W//2, 50+BOSS_H, fill="purple")
    boss_attack_cooldown = 0
    boss_bar = canvas.create_rectangle(0, 0, 0, 0, fill="red")



def overlap(a, b):
    ax1, ay1, ax2, ay2 = canvas.coords(a)
    bx1, by1, bx2, by2 = canvas.coords(b)
    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1



def game_over():
    global game_over_flag
    game_over_flag = True
    canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", font=("Arial", 40, "bold"), fill="red")
    canvas.itemconfig(player, state="hidden")
    for e in enemies:
        canvas.itemconfig(e, state="hidden")
    for b in bullets:
        canvas.itemconfig(b, state="hidden")
    for eb in enemy_bullets:
        canvas.itemconfig(eb['id'], state="hidden")
    if boss:
        canvas.itemconfig(boss, state="hidden")
    if boss_bar:
        canvas.itemconfig(boss_bar, state="hidden")



def update():
    global score, lives, difficulty, stage, boss, boss_health, boss_attack_cooldown, game_over_flag, boss_bar
    global vx, vy, boss_dir, boss_change_cooldown

    if game_over_flag:
        return

    
    x1, y1, x2, y2 = canvas.coords(player)
    if 0 <= x1 + vx <= WIDTH - PLAYER_W:
        canvas.move(player, vx, 0)
    if 0 <= y1 + vy <= HEIGHT - PLAYER_H:
        canvas.move(player, 0, vy)

    
    for b in bullets[:]:
        canvas.move(b, 0, -10)
        if canvas.coords(b)[1] < 0:
            canvas.delete(b)
            bullets.remove(b)

    
    if stage < 3:
        if random.randint(1, max(1, 30 - difficulty)) == 1:
            spawn_enemy()

    
    for e in enemies[:]:
        canvas.move(e, 0, 2 + difficulty*0.5)
        ex1, ey1, ex2, ey2 = canvas.coords(e)
        if ey2 > HEIGHT:
            canvas.delete(e)
            enemies.remove(e)
            lives -= 1
            canvas.itemconfig(lives_text, text=f"Lives: {lives}")
            if lives <= 0:
                game_over()
            continue
        collided = False
        for b in bullets[:]:
            if overlap(e, b):
                canvas.delete(e)
                canvas.delete(b)
                enemies.remove(e)
                bullets.remove(b)
                score += 10
                canvas.itemconfig(score_text, text=f"Score: {score}")
                difficulty = score // 100 + 1
                collided = True
                break
        if collided:
            continue
        if overlap(e, player):
            game_over()
            return

    
    for eb in enemy_bullets[:]:
        canvas.move(eb['id'], eb['vx'], eb['vy'])
        ex1, ey1, ex2, ey2 = canvas.coords(eb['id'])
        if ey2 > HEIGHT or ex2 < 0 or ex1 > WIDTH:
            canvas.delete(eb['id'])
            enemy_bullets.remove(eb)
        elif overlap(player, eb['id']):
            canvas.delete(eb['id'])
            enemy_bullets.remove(eb)
            lives -= 1
            canvas.itemconfig(lives_text, text=f"Lives: {lives}")
            if lives <= 0:
                game_over()

    
    if stage < 3 and score // stage_score + 1 > stage:
        stage += 1
        canvas.itemconfig(stage_text, text=f"Stage: {stage}")
        show_stage_message(stage)

    
    if stage == 3 and boss is None:
        spawn_boss()
        boss_dir = 3
        boss_change_cooldown = 0

    
    if boss:
        canvas.move(boss, 0, 1)
        bx1, by1, bx2, by2 = canvas.coords(boss)
        boss_attack_cooldown += 1
        boss_change_cooldown += 1

        
        if boss_change_cooldown >= 50:
            boss_dir = random.choice([-4, -3, -2, 2, 3, 4])
            boss_change_cooldown = 0
        if 0 <= bx1 + boss_dir and bx2 + boss_dir <= WIDTH:
            canvas.move(boss, boss_dir, 0)

        
        pattern_speed = 4
        bullet_count = 3
        if boss_health <= 20:  
            pattern_speed = 5
            bullet_count = 5
        if boss_health <= 10:  
            pattern_speed = 6
            bullet_count = 7

        
        if boss_attack_cooldown >= 50:
            for i in range(bullet_count):
                angle = -0.3 + i * (0.6/(bullet_count-1)) if bullet_count>1 else 0
                tx = (bx1+bx2)//2 + angle*100
                ty = by2 + 10
                spawn_enemy_bullet((bx1+bx2)//2, by2, tx, ty, speed=pattern_speed)
            boss_attack_cooldown = 0

        
        for b in bullets[:]:
            if overlap(boss, b):
                bullets.remove(b)
                canvas.delete(b)
                boss_health -= 1
                if boss_health <= 0:
                    canvas.create_text(
                        WIDTH//2, HEIGHT//2,
                        text="STAGE CLEARED",
                        font=("Arial", 40, "bold"),
                        fill="yellow"
                    )
                    game_over_flag = True
                    canvas.itemconfig(player, state="hidden")
                    for b2 in bullets:
                        canvas.itemconfig(b2, state="hidden")
                    for eb in enemy_bullets:
                        canvas.itemconfig(eb['id'], state="hidden")
                    canvas.delete(boss)
                    boss = None
                    if boss_bar:
                        canvas.itemconfig(boss_bar, state="hidden")
                break

        if overlap(player, boss):
            game_over()
            return

        
        if boss_bar:
            canvas.delete(boss_bar)
        bar_width = int(BOSS_W * boss_health / 30)
        boss_bar = canvas.create_rectangle(bx1, by1-10, bx1+bar_width, by1-5, fill="red")

    root.after(30, update)


def start_opening():
    global opening_flag
    text = canvas.create_text(WIDTH//2, HEIGHT//2, text="★ SHOOTING GAME ★", font=("Arial", 40, "bold"), fill="yellow")
    def end_opening():
        global opening_flag
        canvas.delete(text)
        opening_flag = False
        update()  
    canvas.after(2000, end_opening)

start_opening()
root.mainloop()
#encoding: utf-8
from cocos import layer
from menus import GameStartMenu,GameOverMenu
from cocos import sprite
import config
from events import fj_event_dispatcher
from roles import Hero
from cocos import audio
from cocos import batch
from roles import EnemySmall
from cocos import collision_model
from cocos import text
from roles import ScoreBoard

class MenuLayer(layer.Layer):
    """
    遮罩层
    """
    is_event_handler = True
    def __init__(self):
        super(MenuLayer,self).__init__()
        bg = sprite.Sprite('imgs/bg.png')
        bg.position = 0,0
        bg.image_anchor = 0,0
        self.add(bg)

class StartMenuLayer(MenuLayer):
    """
    游戏开始层
    """
    def __init__(self):
        super(StartMenuLayer,self).__init__()
        self.game_menu = GameStartMenu()
        self.add(self.game_menu)

        logo = sprite.Sprite('imgs/logo.png')
        logo.position = config.WIN_WIDTH//2,config.WIN_HEIGHT//2+130
        logo.scale = 0.5
        self.add(logo)


class GameOverMenuLayer(MenuLayer):
    """
    游戏结束层
    """
    def __init__(self):
        super(GameOverMenuLayer,self).__init__()
        self.label = text.Label("得分："+str(Hero.score),font_name='Microsoft YaHei',font_size=20,anchor_x='center',anchor_y='center',color=(120,124,125,255))
        self.label.position = config.WIN_WIDTH//2,config.WIN_HEIGHT//2+140
        self.add(self.label)

        self.game_menu = GameOverMenu()
        self.add(self.game_menu)


class GameLayer(layer.Layer):
    """
    游戏层
    """
    is_event_handler = True

    def __init__(self):
        win_width,win_height = config.WIN_WIDTH,config.WIN_HEIGHT
        super(GameLayer,self).__init__()

        self.bg1 = sprite.Sprite('imgs/bg.png')
        self.bg1.image_anchor = 0,0
        self.bg1.position = 0,0

        self.bg2 = sprite.Sprite('imgs/bg.png')
        self.bg2.image_anchor = 0,0
        self.bg2.position = 0,win_height

        # 添加背景
        self.add(self.bg1)
        self.add(self.bg2)

        # 添加自己的飞机
        self.hero = Hero()
        self.add(self.hero,z=1000)

        # 敌机
        self.enemy_batch = batch.BatchNode()
        self.add(self.enemy_batch)
        self.resuable_small_enemy_set = set()
        self.active_small_enemy_set = set()
        self.all_small_enemy_set = set()

        # 积分榜
        self.score_board = ScoreBoard()
        self.add(self.score_board)

        # 碰撞检测
        self.enemy_collision = collision_model.CollisionManagerGrid(0,config.WIN_WIDTH,0,config.WIN_HEIGHT,110,110)
        self.enemy_bullet_collisoin = collision_model.CollisionManagerGrid(0,config.WIN_WIDTH,0,config.WIN_HEIGHT-50,10,10)

        # 消息调度
        self.schedule(self.run)
        self.schedule_interval(self.update_enemy,0.2)

    def run(self,dt):
        """
        每帧都会执行的方法
        """

        # 1. 更新背景图片的位置
        _,bg1_y = self.bg1.position
        bg1_y -= 1

        height = config.WIN_HEIGHT

        if bg1_y <= -height:
            bg1_y = 0

        self.bg1.set_position(0,bg1_y)
        self.bg2.set_position(0,bg1_y+height)

        # 2. 检测有没有敌机碰到自己的飞机
        self.enemy_collision.clear()
        for x in self.all_small_enemy_set:
            self.enemy_collision.add(x)
        result = self.enemy_collision.objs_colliding(self.hero)
        # 如果检测到死亡
        if result:
            self.hero.alive = False
            # 停止敌飞机
            self.stop_enemy()
            # 发送游戏结束事件
            def game_over(dt):
                fj_event_dispatcher.dispatch_event('on_game_over')
            self.schedule_interval(game_over,2.5)

        # 3. 检测子弹和敌机是否碰撞
        self.enemy_bullet_collisoin.clear()
        for x in self.hero.active_bullets:
            self.enemy_bullet_collisoin.add(x)
        for x in self.active_small_enemy_set:
            self.enemy_bullet_collisoin.add(x)
        result = self.enemy_bullet_collisoin.iter_all_collisions()
        for one,two in result:
            if type(one) == type(two):
                continue
            else:
                one.explode()
                two.explode()
                # 加100分
                Hero.score += 100
                # 更新分数
                self.score_board.add_score(100)

    def stop_enemy(self):
        self.unschedule(self.update_enemy)

    def update_enemy(self,dt):
        """
        更新敌机
        """
        small_enemy = None
        if len(self.resuable_small_enemy_set) == 0:
            small_enemy = EnemySmall()
            # self.enemy_collision.add(small_enemy)
            self.all_small_enemy_set.add(small_enemy)
            self.enemy_batch.add(small_enemy,z=999)
        else:
            small_enemy = self.resuable_small_enemy_set.pop()
            print('重用了敌机：',id(small_enemy))

        small_enemy.reset_state()
        self.active_small_enemy_set.add(small_enemy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # 更新飞机的位置
        self.hero.update_position(x,y)

    def on_small_enemy_reuseable(self,enemy):
        # enemy.reset_position()
        self.resuable_small_enemy_set.add(enemy)
        try:
            self.active_small_enemy_set.remove(enemy)
        except:
            pass

    def on_enter(self):
        super(GameLayer,self).on_enter()
        fj_event_dispatcher.push_handlers(self)

    def on_exit(self):
        super(GameLayer,self).on_exit()
        fj_event_dispatcher.remove_handlers(self)
        self.scheduled_calls = []
        self.scheduled_interval_calls = []




#encoding: utf-8

from cocos import sprite
from cocos import batch
from pyglet.image import Animation
import pyglet
import config
from events import fj_event_dispatcher
from cocos import audio
import random
from cocos import collision_model as collision
from cocos import actions
from cocos import text


class Bullet(sprite.Sprite):
    def __init__(self):
        image = 'imgs/bullet.png'
        super(Bullet,self).__init__(image)
        self.scale = 0.5
        # 是否可以重新使用了
        self.reuseable = False
        # cshape
        self.cshape = collision.AARectShape(collision.eu.Vector2(0,0),self.width//2,self.height//2)
        audio.pygame.mixer.init()
        self.audio = audio.pygame.mixer.Sound('sounds/bullet.ogg')
        self.schedule(self.move)

    def move(self,dt):
        x,y = self.position
        y += 8
        self.position = x,y
        self.cshape.center = collision.eu.Vector2(x,y)
        # 如果超过屏幕范围，代表可以重新利用了
        if y > config.WIN_HEIGHT:
            self.reuseable = True
            fj_event_dispatcher.dispatch_event('on_bullet_reuseable',self)

    def fire(self):
        self.audio.play(0,0)

    def explode(self):
        # 移动位置到屏幕外
        self.position = -100,-100
        # 发送事件
        fj_event_dispatcher.dispatch_event('on_bullet_reuseable',self)

class Hero(sprite.Sprite):
    """
    自己的飞机
    """
    __instance = None
    score = 0

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Hero,cls).__new__(cls,*args,**kwargs)
        return cls.__instance

    def __init__(self):
        image = Animation.from_image_sequence(map(lambda x:pyglet.resource.image('imgs/hero/hero%d.png'%x),[x for x in range(1,3)]),0.05,True)
        super(Hero,self).__init__(image)
        self.scale = 0.5
        self.position = config.WIN_WIDTH//2,70
        self._alive = True

        # 精灵batch
        self.batch_bullets = batch.BatchNode()
        self.all_bullets = set()
        self.active_bullets = set()
        self.reuse_bullets = set()

        # cshape
        self.cshape = collision.AARectShape(collision.eu.Vector2(*self.position),self.width//2,self.height//2)

        # 事件调度
        self.schedule_interval(self.fire,0.2)

    def fire(self,dt):
        bullet = None
        if len(self.reuse_bullets) == 0:
            bullet = Bullet()
            self.batch_bullets.add(bullet)
            self.all_bullets.add(bullet)
        else:
            bullet = self.reuse_bullets.pop()
            # print('重复利用子弹：',id(bullet))

        x, y = self.x,self.y + self.height//2
        bullet.position = x, y
        self.active_bullets.add(bullet)
        # 播放声音
        bullet.fire()

    def stop_fire(self):
        self.unschedule(self.fire)

    @property
    def alive(self):
        return self._alive

    @alive.setter
    def alive(self,value):
        # 改变状态
        if self._alive and not value:
            self.die_action()
        self._alive = value

    def die_action(self):
        # 改变被撞的精灵图片
        image = Animation.from_image_sequence(
            map(lambda x: pyglet.resource.image('imgs/hero/hero%d.png' % x), [x for x in range(3, 6)]), 0.05, False)
        self.image = image

        # 停止发射
        self.stop_fire()

        # 播放爆炸的声音
        audio.pygame.mixer.init()
        sound = audio.pygame.mixer.Sound('sounds/hero_die.ogg')
        sound.play(0, 0)

        # 闪几下后消失
        self.do(actions.Blink(2,1)+actions.Hide())

    def update_position(self,x,y):
        self.position = x,y
        self.cshape.center = collision.eu.Vector2(x,y)

    def on_bullet_reuseable(self,bullet):
        self.reuse_bullets.add(bullet)
        try:
            self.active_bullets.remove(bullet)
        except:
            pass

    def on_enter(self):
        super(Hero,self).on_enter()
        self.parent.add(self.batch_bullets)
        fj_event_dispatcher.push_handlers(self)

    def on_exit(self):
        super(Hero,self).on_exit()
        fj_event_dispatcher.remove_handlers(self)

class EnemyBase(sprite.Sprite):
    """
    敌机的父类
    """
    def __init__(self,image):
        super(EnemyBase,self).__init__(image)
        self.fj_image = image
        self.scale = 0.6
        self.cshape = collision.AARectShape(collision.eu.Vector2(*self.position),self.width//2,self.height//2)
        self.reset_position()
        self.schedule(self.run)

    def run(self,dt):
        raise NotImplementedError('请使用Enemy的子类')

    def reset_state(self):
        self.reset_position()
        self.image = pyglet.resource.image(self.fj_image)
        print('image:',self.image)

    def reset_position(self):
        self.position = random.randint(self.width//2+10,config.WIN_WIDTH-self.width//2), config.WIN_HEIGHT + self.height//2
        self.cshape.center = collision.eu.Vector2(*self.position)

    def stop_move(self):
        self.unschedule(self.run)

class EnemySmall(EnemyBase):
    """
    小敌机
    """
    def __init__(self):
        image = 'imgs/enemy/enemy_small1.png'
        super(EnemySmall,self).__init__(image)

    def run(self,dt):
        x,y = self.position
        y -= 5
        self.position = x,y
        self.cshape.center = collision.eu.Vector2(x,y)
        if y < -10:
            # 发送小飞机可用事件
            fj_event_dispatcher.dispatch_event('on_small_enemy_reuseable',self)

    def explode(self):
        # 停止前行
        self.stop_move()
        # 精灵图片
        animation = Animation.from_image_sequence(map(lambda x:pyglet.resource.image('imgs/enemy/enemy_small%d.png'%x),[x for x in range(2,5)]),0.05,False)
        self.image = animation
        # 播放音效
        audio.pygame.mixer.init()
        sound = audio.pygame.mixer.Sound('sounds/enemy_die.ogg')
        sound.play(0,0)
        # 消失
        def disppear(dt):
            self.position = -10,-10
            self.cshape.center = collision.eu.Vector2(-10,-10)
            # 发送重用敌机的事件
            fj_event_dispatcher.dispatch_event('on_small_enemy_reuseable', self)
            self.unschedule(disppear)
        self.schedule_interval(disppear,0.15)

class ScoreBoard(text.Label):
    def __init__(self):
        super(ScoreBoard,self).__init__('0',font_name='Microsoft YaHei',font_size=16,color=(67,68,69,255))
        self.position = 50,config.WIN_HEIGHT-40

    def add_score(self,value):
        old_score = int(self.element.text)
        new_score = old_score + value
        self.element.text = str(new_score)




#encoding: utf-8

from cocos import scene
from layers import StartMenuLayer,GameLayer,GameOverMenuLayer
from cocos import audio

class StartMenuScene(scene.Scene):
    def __init__(self):
        menu_layer = StartMenuLayer()
        super(StartMenuScene,self).__init__(menu_layer)


class GameScene(scene.Scene):
    def __init__(self):
        game_layer = GameLayer()
        super(GameScene,self).__init__(game_layer)

    def on_enter(self):
        super(GameScene,self).on_enter()
        # 播放背景音乐
        audio.pygame.mixer.init()
        # 在Python3中，要encode成bytes类型，这是cocos2d中的一个bug
        audio.pygame.mixer.music.load('sounds/bg_music.mp3'.encode('utf-8'))
        audio.pygame.mixer.music.play(-1, 0)

    def on_exit(self):
        super(GameScene,self).on_exit()
        audio.pygame.mixer.music.stop()

class GameOverScene(scene.Scene):
    def __init__(self):
        super(GameOverScene,self).__init__(GameOverMenuLayer())
#encoding: utf-8


from cocos.director import director
from scenes import StartMenuScene,GameScene,GameOverScene
import config
from events import fj_event_dispatcher
from cocos import scenes

# 游戏开始事件监听
@fj_event_dispatcher.event
def on_game_start():
    director.replace(GameScene())

# 游戏结束事件监听
@fj_event_dispatcher.event
def on_game_over():
    director.replace(GameOverScene())


# 初始化导演类
director.init(width=config.WIN_WIDTH,height=config.WIN_HEIGHT,fullscreen=False,caption='知了飞机')



# 运行第一个场景
director.set_show_FPS(30)
director.run(StartMenuScene())

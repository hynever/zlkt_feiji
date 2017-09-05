#encoding: utf-8
from cocos import menu
from cocos import audio
from cocos import director
from events import fj_event_dispatcher

class FJBaseMenu(menu.Menu):
    """
    游戏菜单的基类
    """
    audio.pygame.mixer.init()
    select_sound = audio.pygame.mixer.Sound('sounds/card.ogg')
    def __init__(self,menu_type,*args,**kwargs):
        super(FJBaseMenu, self).__init__(*args,**kwargs)
        self.font_item['font_size'] = 40
        self.font_item['color'] = 255,255,255
        self.font_item_selected['font_size'] = self.font_item['font_size']
        self.font_item_selected['color'] = 204,204,204

        item_image_path = ''
        if menu_type == 'start':
            item_image_path = 'imgs/btn1.png'
        else:
            item_image_path = 'imgs/btn2.png'
        self.start_menu = menu.ImageMenuItem(item_image_path,self.start_game)
        self.end_menu = menu.ImageMenuItem('imgs/btn3.png',self.end_game)
        self.create_menu([self.start_menu,self.end_menu],selected_effect=menu.shake())

    def start_game(self):
        raise NotImplementedError('请使用BaseMenu的子类')

    def end_game(self):
        # 退出游戏
        director.director.terminate_app = True


class GameStartMenu(FJBaseMenu):
    """
    开始游戏的菜单
    """
    def __init__(self):
        super(GameStartMenu,self).__init__('start')

    def start_game(self):
        print('开始游戏')
        fj_event_dispatcher.dispatch_event('on_game_start')

class GameOverMenu(FJBaseMenu):
    """
    游戏结束后的按钮
    """
    def __init__(self):
        super(GameOverMenu,self).__init__('restart')

    def start_game(self):
        print('重新开始游戏')
        fj_event_dispatcher.dispatch_event('on_game_start')

#encoding: utf-8

from pyglet import event

class FJEventDispatcher(event.EventDispatcher):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(FJEventDispatcher,cls).__new__(cls,*args,**kwargs)
        return cls.__instance

FJEventDispatcher.register_event_type('on_game_start')
FJEventDispatcher.register_event_type('on_game_over')
FJEventDispatcher.register_event_type('on_bullet_reuseable')
FJEventDispatcher.register_event_type('on_small_enemy_reuseable')

# 单例设计模式
fj_event_dispatcher = FJEventDispatcher()
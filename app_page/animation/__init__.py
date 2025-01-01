# app_page/animation/__init__.py
from .FadeEffect import FadeEffect
from .Loading import Loading
from .MoveWin import MoveWin
from .RightClick import RightClick_Menu, Click_RightClick_Menu
from .Shadow import Shadow
from .ShakeEffect import ShakeEffect
from ..animation import ScrollMethod

__all__ = [
  "FadeEffect",
  "Loading",
  "MoveWin",
  "RightClick_Menu",
  "Click_RightClick_Menu",
  "Shadow",
  "ShakeEffect",
  "ScrollMethod"
]
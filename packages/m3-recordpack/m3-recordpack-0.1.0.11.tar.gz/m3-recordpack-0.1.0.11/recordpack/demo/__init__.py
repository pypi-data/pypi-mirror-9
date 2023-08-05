# coding: utf-8
u"""
Приложение, демонстрирующее возможности Recordpack.
"""

#: Патчинг m3_ext
#: --------------
#:
#: В связи с тем, что в m3_blank.urls нет очевидной возможности
#: расширить workspace, патчится workspace с указанием необходимого
#: шаблона, для обеспечения работы "из коробки".
import functools
import m3_ext
m3_ext.workspace = functools.partial(m3_ext.workspace, template='demo_workspace.html')
# -*- coding: utf-8 -*-
from Products.CMFCore.Expression import Expression, getExprContext
from zope.tales.tales import CompilerError


def get_marker_image(context, marker_img):
    try:
        marker_img = Expression(str(marker_img))(getExprContext(context))
    except CompilerError:
        marker_img = "{}/{}".format(context.aboslute_url(), marker_img)
    return marker_img

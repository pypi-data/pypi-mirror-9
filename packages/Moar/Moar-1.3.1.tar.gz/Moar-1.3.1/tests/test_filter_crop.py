# -*- coding: utf-8 -*-
from .utils import assert_image, assert_size
from .test_filters import apply_filter


def test_crop(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop50x90.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 90)
    assert_image(tp, out)


def test_crop_xy_px(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop50x50-100|20.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 50, 100, 20)
    assert_image(tp, out)


def test_crop_xy_short(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop50x50-70.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 50, 70)
    assert_image(tp, out)


def test_crop_xy_pc(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop50x50-30pc|50pc.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 50, '30%', '50%')
    assert_image(tp, out)


def test_crop_xy_center(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop50x50-center.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 50, 'center')
    assert_image(tp, out)


def test_crop_xy_overflow_xy(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop10.png'
    tp = apply_filter(engine, 'crop', ini, out, 50, 50, 190, 130)
    assert_size(tp, 10, 10)


def test_crop_xy_overflow_wh(engine):
    ini = 'a200x140.png'
    out = engine.name + '-crop500x500.png'
    tp = apply_filter(engine, 'crop', ini, out, 500, 500)
    assert_image(tp, out)

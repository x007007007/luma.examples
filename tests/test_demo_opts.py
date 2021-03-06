#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Richard Hull and contributors
# See LICENSE.rst for details.

"""
Tests for the :py:mod:`demo_opts` module.
"""

import os
import sys

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

import luma.emulator.device

from demo_opts import display_settings, get_device, cmdline


test_config_file = os.path.join(os.path.dirname(__file__),
    'resources', 'config-test.txt')


def assertInError(msg, capsys):
    """
    Helper to find text in argparse error output message.
    """
    out, err = capsys.readouterr()
    assert msg in err


def test_display_settings():
    """
    Summary is returned.
    """
    class foo(object):
        display = 'foo'
        interface = 'bar'
        width = 100
        height = 50

    result = display_settings(foo())

    assert result == """Display: foo
Interface: bar
Dimensions: 100 x 50
----------------------------------------"""


def test_get_device_config_file_missing():
    """
    Loading a missing config file throws an error.
    """
    with pytest.raises(IOError):
        get_device(['-f', 'foo'])


def test_get_device_config_file_success():
    """
    Loading a correct config file does not throw an error.
    """
    device = get_device(['-f', test_config_file])

    assert isinstance(device, luma.emulator.device.capture)


def test_get_device_unknown(capsys):
    """
    Load an unknown device.
    """
    test_args = [__name__, '--display', 'foo']
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            get_device()

    assertInError("invalid choice: 'foo'", capsys)


# luma.emulator

def test_get_device_emulator_all():
    """
    Load an emulator device.
    """
    emulators = {
        'capture': luma.emulator.device.capture,
        'pygame': luma.emulator.device.pygame,
        'gifanim': luma.emulator.device.gifanim
    }
    for display, klass in emulators.items():
        device = get_device(['--display', display])
        assert isinstance(device, klass)


# luma.led_matrix

def test_get_device_led_matrix_all(capsys):
    """
    Load supported led_matrix devices one by one.
    """
    for display in cmdline.get_display_types().get('led_matrix'):
        try:
            get_device(['--display', display])
        except SystemExit:
            assertInError('SPI device not found', capsys)
        except ImportError as e:
            pytest.skip(str(e))


# luma.lcd

def test_get_device_lcd_all(capsys):
    """
    Load supported lcd devices one by one.
    """
    for display in cmdline.get_display_types().get('lcd'):
        try:
            get_device(['--display', display])
        except SystemExit:
            try:
                assertInError('error: GPIO access not available', capsys)
            except:
                pass
        except ImportError as e:
            pytest.skip(str(e))


# luma.oled

def test_get_device_oled_all(capsys):
    """
    Load supported oled devices one by one.
    """
    for display in cmdline.get_display_types().get('oled'):
        with pytest.raises(SystemExit):
            get_device(['--display', display])

        assertInError('I2C device', capsys)


def test_get_device_oled_interface_unknown(capsys):
    """
    Get oled device with unknown interface.
    """
    with pytest.raises(SystemExit):
        get_device(['--display', 'ssd1306',
            '--interface', 'foo'])

    assertInError("argument --interface/-i: invalid choice: 'foo'", capsys)

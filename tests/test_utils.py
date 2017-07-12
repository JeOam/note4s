# -*- coding: utf-8 -*-

"""
    test_utils.py
    ~~~~~~~
"""
import pytest
from note4s.utils.mail import sent_mail

@pytest.mark.webtest
def test_mail():
    with open('note4s/utils/registration_code.html') as f:
        content = f.read()
        content = content.replace('registration_code', '123456')
        result = sent_mail(
            from_mail="admin <admin@mg.note4s.com>",
            to_mail="jeoamlx@icloud.com",
            title="Test",
            content=content
        )
        assert result is True
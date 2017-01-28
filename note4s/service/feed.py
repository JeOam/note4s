# -*- coding: utf-8 -*-

"""
    feed.py
    ~~~~~~~
"""

from note4s.models import (
    Activity, N_TARGET_TYPE, N_ACTION,
    Note, Notebook
)


def feed_new_note(user_id, note_id, note_title, notebook_id, session):
    notebook = session.query(Notebook).filter_by(id=notebook_id).one()
    activity = Activity(
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note_title,
        target_owner_id=notebook_id,
        target_owner_type=N_TARGET_TYPE[3],
        target_owner_desc=notebook.name,
        user_id=user_id
    )
    session.add(activity)
    session.commit()


def feed_new_subnote(user_id, note_id, subnote_id, session):
    note = session.query(Note).filter_by(id=note_id).one()
    notification = Activity(
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note.title,
        action=N_ACTION[1],
        user_id=user_id,
        anchor=subnote_id
    )
    session.add(notification)
    session.commit()

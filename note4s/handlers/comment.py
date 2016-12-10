# -*- coding: utf-8 -*-

"""
    comment.py
    ~~~~~~~
"""
from .base import BaseRequestHandler
from note4s.models import Note, Comment, Star, N_TARGET_TYPE
from note4s.service.notify import notify_note_comment_star

class NoteCommentHandler(BaseRequestHandler):
    def get(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        comments = self.session.query(Comment).filter(Comment.note_id == note_id).all()
        result = {}
        result["note"] = note.to_dict()
        result["comments"] = [comment.to_dict() for comment in comments]
        self.api_success_response(result)

    def post(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        params = self.get_params()
        content = params.get("content")
        reply_to = params.get("reply_to")
        if not content:
            self.api_fail_response(f'Invalid comment.')
            return
        comment_count = self.session.query(Comment).filter_by(note_id = note_id).count()
        comment = Comment(content=content,
                          note_id=note_id,
                          user_id=self.current_user.id,
                          index=comment_count + 1,
                          reply_to=reply_to)
        self.session.add(comment)
        self.session.commit()
        self.api_success_response(comment.to_dict())


class StarCommentHandler(BaseRequestHandler):
    def post(self, comment_id):
        comment = self.session.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            self.api_fail_response(f'Comment {comment_id} does not exist.')
            return
        star = self.session.query(Star).filter_by(
            target_id=comment_id,
            target_type=N_TARGET_TYPE[4],
            user_id=self.current_user.id
        ).first()
        star_count = self.session.query(Star).filter_by(
            target_id=comment_id,
            target_type=N_TARGET_TYPE[4]
        ).count()
        if star:
            self.api_success_response(star_count)
            return

        star = Star(target_id=comment_id,
                    target_type=N_TARGET_TYPE[4],
                    user_id=self.current_user.id)
        self.session.add(star)
        self.session.commit()
        if comment.user_id != self.current_user.id:
            notify_note_comment_star(
                note_owner_id=comment.user_id,
                comment_id=comment.id,
                sender_id=self.current_user.id,
                session=self.session
            )
        self.api_success_response(star_count + 1)

    def delete(self, comment_id):
        comment = self.session.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            self.api_fail_response(f'Comment {comment_id} does not exist.')
            return
        comment.is_valid = False
        self.session.delete(comment)
        self.session.commit()
        self.api_success_response(True)

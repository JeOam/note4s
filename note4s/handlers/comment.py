# -*- coding: utf-8 -*-

"""
    comment.py
    ~~~~~~~
"""
from sqlalchemy import asc
from note4s.models import Note, Comment, User
from note4s.service.notify import (
    notify_note_comment,
    notify_comment_reply,
    notify_comment_star,
    notify_comment_mention
)
from .base import BaseRequestHandler


class NoteCommentHandler(BaseRequestHandler):
    def get(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        comments = self.session.query(Comment).filter(
            Comment.note_id == note_id
        ).order_by(
            asc(Comment.index)
        ).all()
        user_ids = [comment.user_id for comment in comments]
        users = self.session.query(User).filter(User.id.in_(user_ids)).all()
        users_info = {user.id.hex: user for user in users}
        result = {}
        result["note"] = note.to_dict()
        result["comments"] = [comment.to_dict() for comment in comments]
        for comment in result["comments"]:
            comment['username'] = users_info[comment["user_id"]].username
            comment['avatar'] = users_info[comment["user_id"]].avatar
            if comment["star_ids"]:
                comment["star_count"] = len(comment["star_ids"])
                if self.current_user.id in comment["star_ids"]:
                    comment["is_star"] = True
                else:
                    comment["is_star"] = False
                del comment["star_ids"]
            else:
                del comment["star_ids"]
                comment["star_count"] = 0
                comment["is_star"] = False
        self.api_success_response(result)

    def post(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        note_owner = self.session.query(User).filter(User.id == note.user_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        params = self.get_params()
        content = params.get("content")
        reply_to = params.get("reply_to")
        mentions = params.get('mentions', [])
        if not content:
            self.api_fail_response(f'Invalid comment.')
            return
        comment_count = self.session.query(Comment).filter_by(note_id=note_id).count()
        comment = Comment(content=content,
                          note_id=note_id,
                          user_id=self.current_user.id,
                          index=comment_count + 1,
                          reply_to=reply_to)
        self.session.add(comment)
        self.session.commit()
        mentions = [username for username in mentions if (note_owner and username != note_owner.username)]
        if len(mentions):
            notify_comment_mention(note_id=note.id,
                                   note_title=note.title,
                                   comment_id=comment.id,
                                   mentions=mentions,
                                   sender_id=self.current_user.id,
                                   session=self.session)
        if reply_to:
            to_comment = self.session.query(Comment).filter_by(id=reply_to).first()
            if to_comment:
                if to_comment.user_id != self.current_user.id:  # 不是自己回复自己的评论
                    notify_comment_reply(
                        to_user_id=to_comment.user_id,
                        comment_id=comment.id,
                        sender_id=self.current_user.id,
                        session=self.session
                    )
                if note.user_id != self.current_user.id:  # 回复的同时，不是在评论自己的笔记
                    notify_note_comment(
                        note_owner_id=note.user_id,
                        note_id=note.id,
                        note_title=note.title,
                        comment_id=comment.id,
                        sender_id=self.current_user.id,
                        session=self.session
                    )
        else:
            if note.user_id != self.current_user.id:
                notify_note_comment(
                    note_owner_id=note.user_id,
                    note_id=note.id,
                    note_title=note.title,
                    comment_id=comment.id,
                    sender_id=self.current_user.id,
                    session=self.session
                )
        self.api_success_response(comment.to_dict())


class StarCommentHandler(BaseRequestHandler):
    def post(self, comment_id):
        comment = self.session.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            self.api_fail_response(f'Comment {comment_id} does not exist.')
            return
        note = self.session.query(Note).filter_by(id=comment.note_id).first()
        if not note:
            self.api_fail_response(f'Note {comment.note_id} does not exist.')
            return
        if self.current_user.id not in comment.star_ids:
            star_ids = [item for item in comment.star_ids]
            star_ids.append(self.current_user.id)
            comment.star_ids = star_ids
        self.session.add(comment)
        self.session.commit()

        if comment.user_id != self.current_user.id:
            notify_comment_star(
                comment_owner_id=comment.user_id,
                note_id=comment.note_id,
                note_title=note.title,
                comment_id=comment.id,
                sender_id=self.current_user.id,
                session=self.session
            )
        self.api_success_response(len(comment.star_ids))

    def delete(self, comment_id):
        comment = self.session.query(Comment).filter_by(id=comment_id).first()
        if not comment:
            self.api_fail_response(f'Comment {comment_id} does not exist.')
            return
        if comment.star_ids:
            comment.star_ids = [item for item in comment.star_ids if item != self.current_user.id]
        self.session.add(comment)
        self.session.commit()
        self.api_success_response(len(comment.star_ids) if comment.star_ids else 0)

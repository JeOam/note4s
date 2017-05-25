# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
import os
import subprocess
import shutil
import tempfile
import requests
from sqlalchemy import or_, and_, asc
from .base import BaseRequestHandler
from note4s.models import Notebook, OWNER_TYPE, User, Organization, \
    Watch, N_TARGET_TYPE, Note, Membership, O_ROLE
from note4s.service.feed import feed_new_notebook, feed_notebook_watch
from note4s.service.notify import notify_notebook_watch


def get_authorized_notebook(self, notebook_id):
    notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
    if not notebook:
        self.api_fail_response(f'Notebook {notebook_id} does not exist.')
        return
    if notebook.owner_type == OWNER_TYPE[0]:
        owner = self.session.query(User).filter_by(id=notebook.owner_id).first()
    else:
        owner = self.session.query(Organization).filter_by(id=notebook.owner_id).first()
    if not owner:
        self.api_fail_response(f'Notebook {notebook_id} does not belong to any user/organization.')
        return
    if notebook.private:
        if not self.current_user:
            self.api_fail_response(f'Notebook {notebook_id} does not exist', 404)
            return
        if notebook.owner_type == OWNER_TYPE[0]:
            if notebook.owner_id != self.current_user.id:
                self.api_fail_response(f'Notebook {notebook_id} does not exist', 404)
                return
        else:
            membership = self.session.query(Membership).filter(
                Membership.organization_id == notebook.owner_id,
                Membership.user_id == self.current_user.id,
                Membership.role != O_ROLE[3]
            ).count()
            if membership == 0:
                self.api_fail_response(f'Notebook {notebook_id} does not exist', 404)
                return
    return notebook, owner


class NotebooksHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        useronly = self.get_argument("useronly", False)
        if username:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                self.api_fail_response(f'User {username} does not exist.')
                return
        elif self.current_user:
            user = self.current_user
        else:
            self.api_success_response([])
            return
        membership_info = {}
        if useronly:
            if self.current_user and self.current_user.username == user.username:
                notebooks = self.session.query(Notebook).filter(
                    Notebook.owner_id == user.id,
                    Notebook.owner_type == OWNER_TYPE[0]
                ).all()
            else:
                notebooks = self.session.query(Notebook).filter(
                    Notebook.owner_id == user.id,
                    Notebook.owner_type == OWNER_TYPE[0],
                    Notebook.private == False
                ).all()
        else:
            memberships = self.session.query(Membership).filter(
                Membership.user_id == user.id,
                Membership.role != O_ROLE[2]
            ).all()
            organization_ids = []
            for membership in memberships:
                organization_ids.append(membership.organization_id)
                membership_info[membership.organization_id] = membership.role
            if self.current_user and self.current_user.username == user.username:
                notebooks = self.session.query(Notebook).filter(
                    or_(
                        and_(
                            Notebook.owner_id == user.id,
                            Notebook.owner_type == OWNER_TYPE[0]
                        ),
                        and_(
                            Notebook.owner_id.in_(organization_ids),
                            Notebook.owner_type == OWNER_TYPE[1]
                        ) if len(organization_ids) > 0 else False
                    )
                ).all()
            else:
                notebooks = self.session.query(Notebook).filter(
                    or_(
                        and_(
                            Notebook.owner_id == user.id,
                            Notebook.owner_type == OWNER_TYPE[0],
                            Notebook.private.is_(False)
                        ),
                        and_(
                            Notebook.owner_id.in_(organization_ids),
                            Notebook.owner_type == OWNER_TYPE[1],
                            Notebook.private.is_(False)
                        ) if len(organization_ids) > 0 else False
                    )
                ).all()
        temp = {}
        result = []
        for notebook in notebooks:
            if notebook.parent_id:
                if temp.get(notebook.parent_id.hex):
                    temp[notebook.parent_id.hex].append(notebook.to_dict())
                else:
                    temp[notebook.parent_id.hex] = [notebook.to_dict()]
            else:
                notebook_info = notebook.to_dict()
                watch_count = self.session.query(Watch).filter_by(
                    target_id=notebook.id,
                    target_type=N_TARGET_TYPE[3]
                ).count()
                notebook_info["type"] = "notebook"
                notebook_info["watch_count"] = watch_count
                if notebook.owner_type == OWNER_TYPE[1]:
                    notebook_info["owner_role"] = membership_info[notebook.owner_id]
                result.append(notebook_info)
        for notebook in result:
            sections = temp.get(notebook["id"], [])
            notebook["children"] = []
            for section in sections:
                section["type"] = "section"
                notes = temp.get(section["id"], [])
                for note in notes:
                    note["type"] = "note"
                section["children"] = notes
                notebook["children"].append(section)
        self.api_success_response(result)

    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name")
        parent_id = params.get('parent_id')
        organization_id = params.get('organization_id')
        private = params.get('private', False)
        if organization_id:
            notebook = Notebook(owner_id=organization_id,
                                owner_type=OWNER_TYPE[1],
                                name=name,
                                parent_id=parent_id,
                                private=private)
        else:
            notebook = Notebook(owner_id=self.current_user.id,
                                owner_type=OWNER_TYPE[0],
                                name=name,
                                parent_id=parent_id,
                                private=private)
        self.session.add(notebook)
        self.session.commit()
        if not parent_id:
            default_section = Notebook(
                owner_id=notebook.owner_id,
                owner_type=notebook.owner_type,
                name='Default Section',
                parent_id=notebook.id,
                private=notebook.private
            )
            self.session.add(default_section)
            self.session.commit()
        if not parent_id and not organization_id and not private:
            feed_new_notebook(
                user_id=self.current_user.id,
                notebook_id=notebook.id,
                session=self.session
            )
        self.api_success_response(notebook.to_dict())


class NotebookHandler(BaseRequestHandler):
    def get(self, notebook_id):
        notebook, owner = get_authorized_notebook(self, notebook_id)
        if not notebook or not owner:
            return
        owner_info = owner.to_dict()
        notebook_ids = self.session.query(Notebook.id).filter(
            Notebook.owner_id == owner.id,
            Notebook.owner_type == notebook.owner_type,
            Notebook.parent_id.is_(None)
        ).all()
        notebook_ids = [notebook[0] for notebook in notebook_ids]
        notebook_count = len(notebook_ids)
        note_count = self.session.query(Note).filter(
            Note.notebook_id.in_(notebook_ids),
            Note.parent_id.is_(None)
        ).count()
        owner_info["notebook_count"] = notebook_count
        owner_info["note_count"] = note_count
        if notebook.owner_type == OWNER_TYPE[0]:
            following_count = self.session.query(Watch).filter_by(
                target_type=N_TARGET_TYPE[0],
                user_id=owner.id,
            ).count()
            follower_count = self.session.query(Watch).filter_by(
                target_type=N_TARGET_TYPE[0],
                target_id=owner.id,
            ).count()
            owner_info["following_count"] = following_count
            owner_info["follower_count"] = follower_count
        else:
            watch_count = self.session.query(Watch).filter(
                Watch.target_id.in_(notebook_ids),
                Watch.target_type == N_TARGET_TYPE[3]
            ).count()
            owner_info["watch_count"] = watch_count

        notebook_info = notebook.to_dict()
        notebook_info["owner"] = owner_info
        notebook_info["owner_type"] = notebook.owner_type
        if self.current_user:
            is_watch = self.session.query(Watch.id).filter(
                Watch.target_id == notebook.id,
                Watch.target_type == N_TARGET_TYPE[3],
                Watch.user_id == self.current_user.id
            ).count()
        else:
            is_watch = 0
        notebook_info["is_watch"] = True if is_watch else False
        watch_count = self.session.query(Watch.id).filter(
            Watch.target_id == notebook.id,
            Watch.target_type == N_TARGET_TYPE[3],
        ).count()
        notebook_info["watch_count"] = watch_count
        sections = self.session.query(Notebook).filter(
            Notebook.parent_id == notebook.id
        ).all()
        notebook_info["children"] = []
        if sections:
            section_ids = [section.id for section in sections]
            notes = self.session.query(Notebook).filter(
                Notebook.parent_id.in_(section_ids)
            ).all()
            section_info = {}
            for index, section in enumerate(sections):
                section_info[section.id] = index
                section_dict = section.to_dict()
                section_dict["children"] = []
                notebook_info["children"].append(section_dict)
            for note in notes:
                index = section_info[note.parent_id]
                notebook_info["children"][index]["children"].append(note.to_dict())
        self.api_success_response(notebook_info)

    def delete(self, notebook_id):
        notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return
        if notebook.owner_type == OWNER_TYPE[0] and notebook.owner_id != self.current_user.id:
            self.api_fail_response('Notebook cannot be deleted because of ownership')
            return
        elif notebook.owner_type == OWNER_TYPE[1]:
            membership = self.session.query(Membership).filter(
                Membership.organization_id == notebook.owner_id,
                Membership.user_id == self.current_user.id,
                Membership.role == O_ROLE[0]
            ).first()
            if not membership:
                self.api_fail_response('Notebook cannot be deleted because of ownership')
                return
        children_notebooks = self.session.query(Notebook).filter_by(parent_id=notebook_id).count()
        if children_notebooks:
            self.api_fail_response('Notebook cannot be deleted because of nonempty')
            return
        section_notes = self.session.query(Note).filter(Note.section_id == notebook_id).all()
        for note in section_notes:
            note.section_id = None
            self.session.add(note)
        notebook_notes = self.session.query(Note).filter(Note.notebook_id == notebook_id).all()
        for note in notebook_notes:
            note.notebook_id = None
            note.section_id = None
            self.session.add(note)
        self.session.delete(notebook)
        self.session.commit()
        self.api_success_response(notebook.to_dict())


class WatchNotebookHandler(BaseRequestHandler):
    def post(self, notebook_id):
        notebook = self.session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return

        watch = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3],
            user_id=self.current_user.id
        ).first()
        watch_count = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3]
        ).count()
        if watch:
            self.api_success_response(watch_count)
            return

        watch = Watch(target_id=notebook_id,
                      target_type=N_TARGET_TYPE[3],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        if notebook.owner_type == OWNER_TYPE[0] and \
                        notebook.owner_id != self.current_user.id:
            notify_notebook_watch(
                notebook_owner_id=notebook.owner_id,
                notebook_id=notebook.id,
                notebook_name=notebook.name,
                sender_id=self.current_user.id,
                session=self.session
            )
        feed_notebook_watch(
            notebook_id=notebook.id,
            user_id=self.current_user.id,
            session=self.session
        )
        self.api_success_response(watch_count + 1)

    def delete(self, notebook_id):
        notebook = self.session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook} does not exist.')
            return
        watch = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3],
            user_id=self.current_user.id
        ).first()
        self.session.delete(watch)
        self.session.commit()
        self.api_success_response(True)


class NotebookPDFHandler(BaseRequestHandler):
    def get(self, notebook_id):
        notebook, owner = get_authorized_notebook(self, notebook_id)
        if not notebook or not owner:
            return
        notebook_info = notebook.to_dict()
        notebook_info["user"] = owner.to_dict()
        sections = self.session.query(Notebook).filter(
            Notebook.parent_id == notebook.id
        ).all()
        notebook_info["children"] = []
        note_ids = []
        if sections:
            section_ids = [section.id for section in sections]
            note_notebooks = self.session.query(Notebook).filter(
                Notebook.parent_id.in_(section_ids)
            ).all()
            section_info = {}
            for index, section in enumerate(sections):
                section_info[section.id] = index
                section_dict = section.to_dict()
                section_dict["children"] = []
                notebook_info["children"].append(section_dict)
            for note_notebook in note_notebooks:
                index = section_info[note_notebook.parent_id]
                notebook_info["children"][index]["children"].append(note_notebook.to_dict())
                note_ids.append(note_notebook.note_id)
        all_notes = self.session.query(Note).filter(
            Note.notebook_id == notebook_id
        ).order_by(asc(Note.created)).all()
        notes = []
        note_info = {}
        for note in all_notes:
            if note.id in note_ids:
                note.children = []
                notes.append(note)
                note_info[note.id] = note
            else:
                parent_note = note_info[note.parent_id]
                parent_note.children.append(note)
        note_files = []
        for note in notes:
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(f'[NOTE4S_TITLE]{note.title}[/NOTE4S_TITLE]'
                    f'[NOTE4S_LABEL]{note.title}[/NOTE4S_LABEL]\n'.encode("utf-8"))
            f.write(f'[NOTE4S_CONTENT]{note.content}[/NOTE4S_CONTENT]\n'.encode("utf-8"))
            f.close()
            f.name
            note_files.append(f.name)
            for subnote in note.children:
                sub_f = tempfile.NamedTemporaryFile(delete=False)
                sub_f.write(f'[NOTE4S_SUBNOTE {subnote.user.username}•{subnote.updated}]'
                            f'{subnote.content}[/NOTE4S_SUBNOTE]\n'.encode("utf-8"))
                sub_f.close()
                sub_f.name
                note_files.append(sub_f.name)
        file_list = ' '.join(note_files)
        cmd_tex = f'pandoc  -f markdown_github --latex-engine=xelatex ' \
                  f'--toc --template=note4s.tex {file_list} -o {notebook_id}.tex'
        p = subprocess.Popen(cmd_tex, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        with open(f'{notebook_id}.tex', "r+") as f:
            content = f.read()

            beginIndex = content.find('{[}NOTE4S\_SUBNOTE')
            while beginIndex != -1:
                endIndex = content[beginIndex:].find('{]}')
                subnote = content[beginIndex: beginIndex + endIndex + 3]
                splits = subnote[19:].split('•')
                username = splits[0]
                time = splits[1][:19]
                content = content.replace(subnote, '\\begin{tcolorbox}[arc=0.1mm, colback=white, ' \
                                                   'colframe=lightgray, coltitle=black, title=' + \
                                                   f'{username} • {time}' + ']\n')
                beginIndex = content.find('{[}NOTE4S\_SUBNOTE')
            content = content.replace('{[}/NOTE4S\_SUBNOTE{]}', '\n\end{tcolorbox}')
            content = content.replace('{[}NOTE4S\_TITLE{]}', '\n\chapter{')
            content = content.replace('{[}/NOTE4S\_TITLE{]}', '}')
            content = content.replace('{[}NOTE4S\_LABEL{]}', '\label{')
            content = content.replace('{[}/NOTE4S\_LABEL{]}', '}\n')
            content = content.replace('{[}NOTE4S\_CONTENT{]}', '')
            content = content.replace('{[}/NOTE4S\_CONTENT{]}', '')

            beginIndex = content.find('\includegraphics{http')
            while beginIndex != -1:
                endIndex = content[beginIndex:].find('}')
                before_url = content[beginIndex: beginIndex + endIndex][17:]
                response = requests.get(before_url, stream=True)
                tmp_file = tempfile.NamedTemporaryFile(delete=False)
                tmp_file.close()
                with open(tmp_file.name, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                content = content[0:beginIndex] + '\includegraphics{' + \
                          tmp_file.name + content[beginIndex + endIndex:]
                note_files.append(tmp_file.name)
                beginIndex = content.find('\includegraphics{http')
            f.seek(0)
            f.write(content)
        cmd_pdf = f'xelatex {notebook_id}.tex'
        p = subprocess.Popen(cmd_pdf, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        with open(f'{notebook_id}.pdf', 'rb') as f:
            self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
            self.set_header("Content-Disposition", f'attachment; filename={notebook_id}.pdf')
            self.write(f.read())
        for note in note_files:
            os.remove(note)
        # os.remove(f'{notebook_id}.tex')
        os.remove(f'{notebook_id}.log')
        os.remove(f'{notebook_id}.pdf')
        os.remove(f'{notebook_id}.aux')
        os.remove(f'{notebook_id}.out')
        os.remove(f'{notebook_id}.toc')
        self.finish()

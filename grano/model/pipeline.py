from datetime import datetime

from grano.core import db, url_for
from grano.model.util import MutableDict, JSONEncodedDict
from grano.model.common import IntBase


# this is based on OpenSpending, see:
# https://github.com/openspending/openspending/blob/master/openspending/model/run.py


class Pipeline(db.Model, IntBase):
    __tablename__ = 'grano_pipeline'

    operation = db.Column(db.Unicode)
    status = db.Column(db.Unicode)
    percent_complete = db.Column(db.Integer)

    project_id = db.Column(db.Integer, db.ForeignKey('grano_project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('grano_account.id'))

    config = db.Column(MutableDict.as_mutable(JSONEncodedDict))

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    entries = db.relationship('LogEntry', backref='pipeline', lazy='dynamic',
        cascade='all, delete, delete-orphan')


    def to_dict_index(self):
        return {
            'id': self.id,
            'project': self.project.to_dict_index() if self.project else None,
            'author': self.author.to_dict_index(),
            'api_url': url_for('pipelines_api.view', id=self.id),
            'operation': self.operation,
            'status': self.status,
            'created_at': self.created_at, 
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'details': self.details,
            'percent_complete': self.percent_complete
        }


    def to_dict(self):
        """ Full serialization of the file metadata. """
        data = self.to_dict_index()
        #data['config'] = self.config
        return data


class LogEntry(db.Model, IntBase):
    __tablename__ = 'grano_log_entry'

    pipeline_id = db.Column(db.Integer, db.ForeignKey('grano_pipeline.id'))
    
    level = db.Column(db.Unicode)
    message = db.Column(db.Unicode)
    error = db.Column(db.Unicode)

    details = db.Column(MutableDict.as_mutable(JSONEncodedDict))


    def to_dict_index(self):
        return {
            'id': self.id,
            'level': level,
            'message': message,
            'error': self.operation,
            'api_url': url_for('log_entries_api.view_entry',
                pipeline_id=self.pipeline.id, id=self.id),
            'created_at': self.created_at, 
            'updated_at': self.updated_at
        }


    def to_dict(self):
        """ Full serialization of the file metadata. """
        data = self.to_dict_index()
        data['details'] = self.details
        return data

import copy
import json
import os
import sys

from flask import jsonify
from flask import request
from flask.ext.api import status
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS
import flask


app = flask.Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'sqlite:///../tokens.db'
)
app.config['SQLALCHEMY_ECHO'] = bool(os.environ.get('SQLALCHEMY_ECHO', True))
app.config['DEBUG'] = bool(os.environ.get('DEBUG', True))
app.config['HOST'] = os.environ.get('HOST', '0.0.0.0')
app.config['PORT'] = int(os.environ.get('PORT', 5000))

db = SQLAlchemy(app)


# Copyright Ferry Boender, released under the MIT license.
def deepupdate(target, src):
    """Deep update target dict with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it.

    Examples:
    >>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> print t
    {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi', 'gaming']}
    """
    for k, v in src.items():
        if type(v) == list:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        elif type(v) == set:
            if not k in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)


class EmailToken(db.Model):
    """Model to store the indexed tokens"""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(1024))
    token = db.Column(db.String(1024))
    token_type = db.Column(db.String(1024))
    token_metadata = db.Column(db.String(2048))
    disabled = db.Column(db.Boolean, default=False)

    def get_token_metadata(self):
        if self.token_metadata:
            return json.loads(self.token_metadata)
        return None

    def as_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'token': self.token,
            'type': self.token_type,
            'metadata': self.get_token_metadata(),
            'disabled': self.disabled,
        }

    @classmethod
    def from_json(cls, data):
        metadata = data.get('metadata')
        try:
            metadata = json.dumps(metadata)
        except TypeError as err:
            print('Error dumping metadata', err, file=sys.stderr)

        return cls(
            subject=data.get('subject'),
            token=data.get('token'),
            token_type=data.get('type'),
            token_metadata=metadata,
            disabled=data.get('disabled', False),
        )

    @classmethod
    def jsonify_all(cls, token_type=None):
        if token_type:
            print('Filtering query by token type', file=sys.stderr)
            results = cls.query.filter_by(token_type=token_type).all()
        else:
            results = cls.query.all()
        return jsonify(tokens=[token.as_dict() for token in results])


@app.route('/')
def check():
    return 'OK'


@app.route('/token', methods=['POST'])
def create_tokens():
    """Creates a token from posted JSON request"""
    new_token = EmailToken.from_json(request.get_json(force=True))

    existing_token = EmailToken.query.filter_by(
        token=new_token.token,
        token_type=new_token.token_type,
    ).first()

    print(
        'Received token with value {} and type {}'.format(
            new_token.token,  new_token.token_type
        ), file=sys.stderr
    )

    print('Existing token? ', existing_token, file=sys.stderr)

    if not existing_token:
        print('No existing token, creating a new one', file=sys.stderr)
        db.session.add(new_token)
        db.session.commit()
        db.session.refresh(new_token)
        return jsonify(
            success=True,
            created=True,
            record=new_token.as_dict()
        )
    else:
        print('Found an existing token', file=sys.stderr)
        # Compute the updated token_metadata dict
        updated_metadata = json.loads(existing_token.token_metadata)
        deepupdate(updated_metadata, request.get_json(force=True)['metadata'])
        # Update the existing token
        existing_token.token_metadata = json.dumps(updated_metadata)
        db.session.commit()
        db.session.refresh(existing_token)
        return jsonify(
            success=True,
            created=False,
            record=existing_token.as_dict()
        )


@app.route('/token', methods=['GET'])
def list_all_tokens():
    """Lists all tokens with an optional type filter"""
    token_type = request.args.get('filter_type')
    print('Asked to filter by ', token_type, file=sys.stderr)
    return EmailToken.jsonify_all(token_type=token_type)


@app.route('/token/<string:token_id>', methods=['GET'])
def get_token(token_id):
    """Gets a token by its primary key id"""
    token = EmailToken.query.filter_by(token=token_id).first()
    if token:
        return jsonify(token.as_dict())
    else:
        return jsonify({}), status.HTTP_404_NOT_FOUND


if __name__ == '__main__':
    db.create_all()
    app.run(host=app.config['HOST'], port=app.config['PORT'])

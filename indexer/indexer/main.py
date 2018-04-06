import json
import os
import sys

from flask import jsonify
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import flask


app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'sqlite:///../tokens.db'
)
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG'] = True

db = SQLAlchemy(app)

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
    def jsonify_all(cls, token_type=None, desc=False):
        query = cls.query
        if token_type:
            print('Filtering query by token type', file=sys.stderr)
            query = query.filter_by(token_type=token_type)
        if desc:
            query = query.order_by(cls.id.desc())
        return jsonify(tokens=[token.as_dict() for token in query.all()])


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
        return jsonify(
            success=True,
            created=False,
            record=existing_token.as_dict()
        )


@app.route('/token', methods=['GET'])
def list_all_tokens():
    """Lists all tokens with an optional type filter"""
    token_type = request.args.get('filter_type')
    desc = request.args.get('desc', False)
    print('Asked to filter by ', token_type, file=sys.stderr)
    return EmailToken.jsonify_all(token_type=token_type, desc=desc)


@app.route('/token/<int:token_id>', methods=['GET'])
def get_token(token_id):
    """Gets a token by its primary key id"""
    token = EmailToken.query.get(token_id)
    return jsonify(token.as_dict())


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5000)

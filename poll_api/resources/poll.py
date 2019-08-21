from flask_restful import Resource, fields, marshal_with
from pollbot.models import Poll
from pollbot.db import get_session

poll_resource_fields = {
    'uuid': fields.String,
    # 'uri': fields.Url('todo_ep')
    'name': fields.String,
    'description': fields.String,
    'locale': fields.String,
    'poll_type': fields.String,
    'number_of_votes': fields.Integer,
    'anonymous': fields.Boolean,
    'results_visible': fields.Boolean,
    'due_date': fields.DateTime(dt_format='iso8601'),
    'allow_new_options': fields.Boolean,
    'european_date_format': fields.Boolean,
    'option_sorting': fields.String,
    'user_sorting': fields.String,
    'created': fields.Boolean,
    'closed': fields.Boolean
    # TODO: Votes, Options, optional: User
}

class PollResource(Resource):
    @marshal_with(poll_resource_fields)
    def get(self):
        # print("debug")
        # return {'asd':'asd'}
        session = get_session()
        polls = session.query(Poll) \
            .filter(Poll.created.is_(True)) \
            .filter(Poll.closed.is_(False)) \
            .all()
            # .filter(Poll.user == user) TODO
        print(polls)
        return polls

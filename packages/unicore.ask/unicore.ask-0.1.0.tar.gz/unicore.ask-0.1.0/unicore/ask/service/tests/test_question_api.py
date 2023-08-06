import uuid

from unicore.ask.service.tests import DBTestCase
from unicore.ask.service.models import QuestionOption, Question


class QuestionApiTestCase(DBTestCase):
    def create_question_option(self, session=None, **attrs):
        return self.create_model_object(QuestionOption, session, **attrs)

    def create_question(self, session=None, **attrs):
        return self.create_model_object(Question, session, **attrs)

    def setUp(self):
        super(QuestionApiTestCase, self).setUp()
        self.question_1 = self.create_question(
            self.db, title='What is your name', short_name='name',
            question_type='free_text',
            options=[])
        self.db.flush()
        self.question_1_option = self.create_question_option(
            self.db, question_id=self.question_1.uuid)

        self.question_2 = self.create_question(
            self.db, title='What is your age', short_name='age',
            question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.create_question_option(
            self.db, title='<18', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='18-29', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='30-49', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='50+', question_id=self.question_2.uuid)

        self.question_3 = self.create_question(
            self.db, title='Which sports do you watch', short_name='sports',
            multiple=True, question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.create_question_option(
            self.db, title='cricket', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='rugby', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='soccer', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='tennis', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='other', question_id=self.question_3.uuid)

        self.db.commit()

    def test_uuid(self):
        the_uuid = self.question_1._uuid
        self.assertEqual(the_uuid, uuid.UUID(self.question_1.uuid))
        self.question_1.uuid = self.question_1.uuid
        self.assertEqual(the_uuid, self.question_1._uuid)
        self.question_1.uuid = uuid.UUID(self.question_1.uuid)
        self.assertEqual(the_uuid, self.question_1._uuid)

    def test_question_not_found(self):
        self.app.get('/questions/%s' % uuid.uuid4(), status=404)

    def test_free_text_question(self):
        resp = self.app.get(
            '/questions/%s' % self.question_1.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_1.to_dict())

    def test_multiple_choice_question(self):
        resp = self.app.get(
            '/questions/%s' % self.question_2.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_2.to_dict())

    def test_multiple_choice_question_with_multiple_response(self):
        resp = self.app.get(
            '/questions/%s' % self.question_3.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_3.to_dict())

    def test_edit(self):
        # change non-privileged fields
        resp = self.app.put_json(
            '/questions/%s' % uuid.uuid4().hex,
            params={'title': 'foo2'})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, {})

    def test_create(self):
        data = {'title': 'foobar'}
        resp = self.app.post_json(
            '/questions', params=data)
        self.assertEqual(resp.json_body, {})

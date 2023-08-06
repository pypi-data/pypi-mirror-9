from uuid import uuid4, UUID

from sqlalchemy import Column, Unicode, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


from unicore.ask.service import Base


class UUIDMixin(object):
    _uuid = Column(
        UUIDType(binary=False), name='uuid', default=uuid4,
        primary_key=True)

    @property
    def uuid(self):
        return self._uuid.hex

    @uuid.setter
    def uuid(self, value):
        if isinstance(value, UUID):
            self._uuid = value
        else:
            self._uuid = UUID(hex=value)


class QuestionResponse(Base, UUIDMixin):
    __tablename__ = 'question_responses'

    text = Column(Unicode(255), nullable=False)
    question_option_id = Column(
        UUIDType(binary=False), ForeignKey('question_options.uuid'),
        nullable=False)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'text': self.text,
        }


class QuestionOption(Base, UUIDMixin):
    __tablename__ = 'question_options'

    title = Column(Unicode(255), nullable=True)
    short_name = Column(Unicode(255), nullable=True)
    responses_count = Column(Integer())
    question_id = Column(
        UUIDType(binary=False), ForeignKey('questions.uuid'), nullable=False)
    responses = relationship(
        QuestionResponse, backref='question_options', lazy="dynamic")

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'short_name': self.short_name,
            'responses_count': self.responses_count,
        }


class Question(Base, UUIDMixin):
    __tablename__ = 'questions'

    question_types = (
        'free_text',
        'multiple_choice',
    )

    title = Column(Unicode(255), nullable=False)
    short_name = Column(Unicode(255), nullable=True)
    multiple = Column(Boolean(255), default=True)
    question_type = Column(Unicode(255), nullable=False)
    options = relationship(QuestionOption, backref='questions', lazy="dynamic")

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'title': self.title,
            'short_name': self.short_name,
            'multiple': self.multiple,
            'question_type': self.question_type,
            'options': [option.to_dict() for option in self.options]
        }

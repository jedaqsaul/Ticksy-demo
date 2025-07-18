"""empty message

Revision ID: ccd0f25735e2
Revises: 6939021ed528
Create Date: 2025-07-18 18:56:49.970374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccd0f25735e2'
down_revision = '6939021ed528'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('event_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('fk_messages_recipient_id_users', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_messages_event_id_events'), 'events', ['event_id'], ['id'])
        batch_op.drop_column('subject')
        batch_op.drop_column('recipient_id')
        batch_op.drop_column('read_status')
        batch_op.drop_column('body')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('body', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('read_status', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('recipient_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('subject', sa.VARCHAR(), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_messages_event_id_events'), type_='foreignkey')
        batch_op.create_foreign_key('fk_messages_recipient_id_users', 'users', ['recipient_id'], ['id'])
        batch_op.drop_column('event_id')
        batch_op.drop_column('content')

    # ### end Alembic commands ###

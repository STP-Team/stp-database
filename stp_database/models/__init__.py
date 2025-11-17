"""Импорт моделей."""

from stp_database.models.Gifter.events import Event as Event
from stp_database.models.Gifter.user import User as User
from stp_database.models.Gifter.users_events import UserEvent as UserEvent
from stp_database.models.KPI.head_premium import HeadPremium as HeadPremium
from stp_database.models.KPI.spec_kpi import SpecKPI as SpecKPI
from stp_database.models.KPI.spec_premium import SpecPremium as SpecPremium
from stp_database.models.Questioner.messages_pair import MessagesPair as MessagesPair
from stp_database.models.Questioner.question import Question as Question
from stp_database.models.Questioner.settings import Settings as Settings
from stp_database.models.Recruitments.candidates import Candidate as Candidate
from stp_database.models.STP.achievement import Achievement as Achievement
from stp_database.models.STP.broadcast import Broadcast as Broadcast
from stp_database.models.STP.employee import Employee as Employee
from stp_database.models.STP.event_log import EventLog as EventLog
from stp_database.models.STP.exchange import Exchange as Exchange
from stp_database.models.STP.exchange import (
    ExchangeSubscription as ExchangeSubscription,
)
from stp_database.models.STP.file import File as File
from stp_database.models.STP.group import Group as Group
from stp_database.models.STP.group_member import GroupMember as GroupMember
from stp_database.models.STP.product import Product as Product
from stp_database.models.STP.purchase import Purchase as Purchase
from stp_database.models.STP.transactions import Transaction as Transaction

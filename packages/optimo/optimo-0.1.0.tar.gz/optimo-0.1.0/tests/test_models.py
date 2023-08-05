# -*- coding: utf-8 -*-
import json
import pytest
from datetime import datetime
from numbers import Number

from optimo import (
    WorkShift,
    Driver,
    Order,
    RoutePlan,
    Break,
    SchedulingInfo,
    TimeWindow,
)
from optimo.errors import OptimoValidationError
from optimo.util import OptimoEncoder

from tests.schema.v1 import (
    BreakValidator,
    DriverValidator,
    OrderValidator,
    RoutePlanValidator,
    WorkShiftValidator,
    SchedulingInfoValidator,
    TimeWindowValidator,
)


jsonify = lambda o: json.dumps(o, cls=OptimoEncoder)
dictify = lambda o: json.loads(jsonify(o))

TYPE_ERR_MSG = "'{}.{}' must be of type {!r}, not {!r}"


dtime = datetime(year=2014, month=12, day=5, hour=8, minute=0)


class TestBreak(object):
    @pytest.fixture
    def cls_name(self):
        return Break.__name__

    def test_earliest_start(self, cls_name):
        brk = Break(earliest_start=3, latest_start=4, duration=5)
        with pytest.raises(TypeError) as excinfo:
            brk.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'earliest_start', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_end_break(self, cls_name):
        brk = Break(earliest_start=dtime, latest_start=4, duration=5)
        with pytest.raises(TypeError) as excinfo:
            brk.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'latest_start', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_duration(self, cls_name):
        brk = Break(earliest_start=dtime, latest_start=dtime, duration=5.5)
        with pytest.raises(TypeError) as excinfo:
            brk.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'duration', (int, long), float)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        brk = Break(earliest_start=dtime, latest_start=dtime, duration=5)
        assert brk.validate() is None

        assert jsonify(brk) == '{"breakStartTo": "2014-12-05T08:00", ' \
                               '"breakStartFrom": "2014-12-05T08:00", ' \
                               '"breakDuration": 5}'

        assert BreakValidator.validate(dictify(brk)) is None


class TestWorkShift(object):
    @pytest.fixture
    def cls_name(self):
        return WorkShift.__name__

    def test_start_work(self, cls_name):
        ws = WorkShift(start_work=3, end_work=4)
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'start_work', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_end_work(self, cls_name):
        ws = WorkShift(start_work=dtime, end_work=3)
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'end_work', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_allowed_overtime(self, cls_name):
        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2.5
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'allowed_overtime', (int, long), float)
        assert err_msg == str(excinfo.value)

    def test_break(self, cls_name):
        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2
        ws.break_ = 42
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'break_', Break, int)
        assert err_msg == str(excinfo.value)

    def test_unavailable_times(self, cls_name):
        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2
        ws.break_ = Break(earliest_start=dtime, latest_start=dtime, duration=5)
        ws.unavailable_times = 3
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'unavailable_times', (list, tuple), int)
        assert err_msg == str(excinfo.value)

        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2
        ws.break_ = Break(earliest_start=dtime, latest_start=dtime, duration=5)
        ws.unavailable_times = [3]
        with pytest.raises(TypeError) as excinfo:
            ws.validate()
        err_msg = "'{}.unavailable_times' must contain elements of type " \
                  "TimeWindow".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2
        assert ws.validate() is None

        ws = WorkShift(start_work=dtime, end_work=dtime)
        ws.allowed_overtime = 2
        ws.break_ = Break(earliest_start=dtime, latest_start=dtime, duration=5)
        ws.unavailable_times = [TimeWindow(start_time=dtime, end_time=dtime)]
        assert ws.validate() is None
        assert jsonify(ws) == (
            '{"workTimeFrom": "2014-12-05T08:00", "break": {"breakStartTo": '
            '"2014-12-05T08:00", "breakStartFrom": "2014-12-05T08:00", '
            '"breakDuration": 5}, "unavailableTimes": [{"timeFrom": '
            '"2014-12-05T08:00", "timeTo": "2014-12-05T08:00"}], "workTimeTo": '
            '"2014-12-05T08:00", "allowedOvertime": 2}'
        )

        assert WorkShiftValidator.validate(dictify(ws)) is None


class TestSchedulingInfo(object):
    @pytest.fixture
    def cls_name(self):
        return SchedulingInfo.__name__

    def test_scheduled_at(self, cls_name):
        si = SchedulingInfo(scheduled_at=1, scheduled_driver=1)
        with pytest.raises(TypeError) as excinfo:
            si.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'scheduled_at', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_scheduled_driver(self, cls_name):
        si = SchedulingInfo(scheduled_at=dtime, scheduled_driver=1)
        with pytest.raises(TypeError) as excinfo:
            si.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'scheduled_driver', (basestring, Driver), int)
        assert err_msg == str(excinfo.value)

        # test it accepts a string as a driver
        si = SchedulingInfo(scheduled_at=dtime, scheduled_driver='bobos')
        assert si.validate() is None

        # test it accepts a driver object too
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        si = SchedulingInfo(scheduled_at=dtime, scheduled_driver=drv)
        assert si.validate() is None


    def test_locked(self, cls_name):
        si = SchedulingInfo(scheduled_at=dtime, scheduled_driver='bobos', locked=4)
        with pytest.raises(TypeError) as excinfo:
            si.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'locked', bool, int)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        si = SchedulingInfo(scheduled_at=dtime, scheduled_driver='bobos')
        assert si.validate() is None
        assert jsonify(si) == (
            '{"scheduledAt": "2014-12-05T08:00", "locked": false, '
            '"scheduledDriver": "bobos"}'
        )
        assert SchedulingInfoValidator.validate(dictify(si)) is None

        # test that if we give a Driver object instead of its string id it has
        # the same result
        drv = Driver(id='bobos', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        si = SchedulingInfo(dtime, drv)
        assert si.validate() is None
        assert jsonify(si) == (
            '{"scheduledAt": "2014-12-05T08:00", "locked": false, '
            '"scheduledDriver": "bobos"}'
        )
        assert SchedulingInfoValidator.validate(dictify(si)) is None


class TestTimeWindow(object):
    @pytest.fixture
    def cls_name(self):
        return TimeWindow.__name__

    def test_start_time(self, cls_name):
        tw = TimeWindow(start_time=2, end_time=3)
        with pytest.raises(TypeError) as excinfo:
            tw.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'start_time', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_end_time(self, cls_name):
        tw = TimeWindow(start_time=dtime, end_time=3)
        with pytest.raises(TypeError) as excinfo:
            tw.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'end_time', datetime, int)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        tw = TimeWindow(start_time=dtime, end_time=dtime)
        assert tw.validate() is None
        assert jsonify(tw) == '{"timeFrom": "2014-12-05T08:00", ' \
                              '"timeTo": "2014-12-05T08:00"}'

        assert TimeWindowValidator.validate(dictify(tw)) is None


class TestOrder(object):
    @pytest.fixture
    def cls_name(self):
        return Order.__name__

    def test_id(self, cls_name):
        order = Order(id=3, lat=5, lng=6, duration=7)
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'id', str, int)
        assert err_msg == str(excinfo.value)

        order = Order(id='', lat='5', lng='6', duration='7')
        with pytest.raises(ValueError) as excinfo:
            order.validate()
        err_msg = "'{}.{}' cannot be empty".format(cls_name, 'id')
        assert err_msg == str(excinfo.value)

    def test_lat(self, cls_name):
        order = Order(id='3', lat='5', lng='6', duration='7')
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'lat', Number, str)
        assert err_msg == str(excinfo.value)

    def test_lng(self, cls_name):
        order = Order(id='3', lat=5, lng='6', duration='7')
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'lng', Number, str)
        assert err_msg == str(excinfo.value)

    def test_duration(self, cls_name):
        order = Order(id='3', lat=5, lng=6, duration='7')
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'duration', (int, long), str)
        assert err_msg == str(excinfo.value)

        order = Order(id='3', lat=5, lng=6, duration=-1)
        with pytest.raises(ValueError) as excinfo:
            order.validate()
        err_msg = "'{}.duration' cannot be negative".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_time_window(self, cls_name):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = 'Foo'
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'time_window', TimeWindow, str)
        assert err_msg == str(excinfo.value)

    def test_priority(self, cls_name):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(start_time=dtime, end_time=dtime)
        order.priority = 3
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'priority', basestring, int)
        assert err_msg == str(excinfo.value)

        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(dtime, dtime)
        order.priority = 'F'
        with pytest.raises(ValueError) as excinfo:
            order.validate()
        err_msg = "'{}.{}' must be one of {}".format(cls_name, 'priority',
                                                     "('L', 'M', 'H', 'C')")
        assert err_msg == str(excinfo.value)

    def test_skills(self, cls_name):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(dtime, dtime)
        order.skills = 'handy'
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'skills', (list, tuple), str)
        assert err_msg == str(excinfo.value)

        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(dtime, dtime)
        order.skills = ['handy', 3]
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = "'{}.skills' must contain elements of type str".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_assigned_to(self, cls_name):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(dtime, dtime)
        order.skills = ['handy', 'quiet']
        order.assigned_to = 4
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'assigned_to', (basestring, Driver), int)
        assert err_msg == str(excinfo.value)

        # test it accepts a string as a driver
        order.assigned_to = 'rantanplan'
        assert order.validate() is None

        # test it accepts a driver objects too
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        order.assigned_to = drv
        assert order.validate() is None

    def test_scheduling_info(self, cls_name):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(dtime, dtime)
        order.skills = ['handy', 'quiet']
        order.assigned_to = 'Tom & Jerry'
        order.scheduling_info = 45
        with pytest.raises(TypeError) as excinfo:
            order.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'scheduling_info', SchedulingInfo, int)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        order = Order(id='3', lat=5.2, lng=6.1, duration=7)
        order.time_window = TimeWindow(start_time=dtime, end_time=dtime)
        order.skills = ['handy', 'quiet']
        order.assigned_to = Driver(id='Tom & Jerry', start_lat=3, start_lng=4,
                                   end_lat=5, end_lng=6)
        order.scheduling_info = SchedulingInfo(scheduled_at=dtime, scheduled_driver='rantanplan')
        assert order.validate() is None
        assert jsonify(order) == (
            '{"assignedTo": "Tom & Jerry", "skills": ["handy", "quiet"], "tw": '
            '{"timeFrom": "2014-12-05T08:00", "timeTo": "2014-12-05T08:00"}, '
            '"lon": 6.1, "priority": "M", "duration": 7, "lat": 5.2, '
            '"schedulingInfo": {"scheduledAt": "2014-12-05T08:00", "locked": '
            'false, "scheduledDriver": "rantanplan"}, "id": "3"}'
        )
        assert OrderValidator.validate(dictify(order)) is None


class TestDriver(object):
    @pytest.fixture
    def cls_name(self):
        return Driver.__name__

    def test_id(self, cls_name):
        drv = Driver(id=3, start_lat='3', start_lng='4', end_lat='4', end_lng='5')
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'id', basestring, int)
        assert err_msg == str(excinfo.value)

        drv = Driver(id='', start_lat='3', start_lng='4', end_lat='4', end_lng='5')
        with pytest.raises(ValueError) as excinfo:
            drv.validate()
        err_msg = "'{}.id' cannot be empty".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_start_lat(self, cls_name):
        drv = Driver(id='3', start_lat='3', start_lng='4', end_lat='4', end_lng='5')
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'start_lat', Number, str)
        assert err_msg == str(excinfo.value)

    def test_start_lng(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng='4', end_lat='4', end_lng='5')
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'start_lng', Number, str)
        assert err_msg == str(excinfo.value)

    def test_end_lat(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat='4', end_lng='5')
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'end_lat', Number, str)
        assert err_msg == str(excinfo.value)

    def test_end_lng(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng='5')
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'end_lng', Number, str)
        assert err_msg == str(excinfo.value)

    def test_work_shifts(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = 4
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'work_shifts', (list, tuple), int)
        assert err_msg == str(excinfo.value)

        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = []
        with pytest.raises(ValueError) as excinfo:
            drv.validate()
        err_msg = "'{}.work_shifts' must contain at least 1 element".\
            format(cls_name)
        assert err_msg == str(excinfo.value)

        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = [3]
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = "'{}.work_shifts' must contain elements of type WorkShift".\
            format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_skills(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv.skills = 3
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'skills', (list, tuple), int)
        assert err_msg == str(excinfo.value)

        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv.skills = [2]
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = "'{}.skills' must contain elements of type str".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_speed_factor(self, cls_name):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv.skills = ['calm', 'angry']
        drv.speed_factor = '4'
        with pytest.raises(TypeError) as excinfo:
            drv.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'speed_factor', Number, str)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self):
        drv = Driver(id='3', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv.skills = ['calm', 'angry']
        drv.speed_factor = 1.5
        assert drv.validate() is None
        assert jsonify(drv) == (
            '{"endLon": 5, "skills": ["calm", "angry"], "endLat": 4, '
            '"startLat": 3, "workShifts": [{"workTimeFrom": "2014-12-05T08:00",'
            ' "workTimeTo": "2014-12-05T08:00"}], "speedFactor": 1.5, '
            '"startLon": 4, "id": "3"}'
        )
        assert DriverValidator.validate(dictify(drv)) is None


class TestRoutePlan(object):
    @pytest.fixture
    def routeplan(self):
        routeplan = RoutePlan(request_id='1234', callback_url='http://someurl',
                              status_callback_url='http://somestatusurl')
        return routeplan

    @pytest.fixture
    def orders(self):
        order1 = Order('3', 5.2, 6.1, 7)
        order1.time_window = TimeWindow(start_time=dtime, end_time=dtime)
        order1.skills = ['handy', 'quiet']
        order1.assigned_to = 'Tom & Jerry'
        order1.scheduling_info = SchedulingInfo(scheduled_at=dtime, scheduled_driver='rantanplan')

        order2 = Order('4', 5.2, 6.1, 7)
        order2.time_window = TimeWindow(start_time=dtime, end_time=dtime)
        order2.skills = ['barista', 'terrorista']
        order2.assigned_to = 'Sam & Max'
        order2.scheduling_info = SchedulingInfo(scheduled_at=dtime, scheduled_driver='rantanplan')
        return order1, order2

    @pytest.fixture
    def drivers(self):
        drv1 = Driver(id='Tom & Jerry', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv1.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv1.skills = ['calm', 'angry']

        drv2 = Driver(id='Sam & Max', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv2.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv2.skills = ['pirate', 'ninja']

        drv3 = Driver(id='rantanplan', start_lat=3, start_lng=4, end_lat=4, end_lng=5)
        drv3.work_shifts = [WorkShift(start_work=dtime, end_work=dtime)]
        drv3.skills = ['woofing', 'barking']
        return drv1, drv2, drv3

    @pytest.fixture
    def cls_name(self):
        return RoutePlan.__name__

    def test_request_id(self, cls_name):
        routeplan = RoutePlan(request_id=1234, callback_url=4, status_callback_url=4)
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'request_id', basestring, int)
        assert err_msg == str(excinfo.value)

        routeplan = RoutePlan(request_id='', callback_url=4, status_callback_url=4)
        with pytest.raises(ValueError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.request_id' cannot be an empty string".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_callback_url(self, cls_name):
        routeplan = RoutePlan(request_id='1234', callback_url=4, status_callback_url=4)
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'callback_url', basestring, int)
        assert err_msg == str(excinfo.value)

    def test_status_callback_url(self, cls_name):
        routeplan = RoutePlan(request_id='1234', callback_url='http://someurl',
                              status_callback_url=4)
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'status_callback_url', basestring, int)
        assert err_msg == str(excinfo.value)

    def test_orders(self, cls_name, routeplan):
        routeplan.orders = 4
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'orders', (list, tuple), int)
        assert err_msg == str(excinfo.value)

        routeplan = RoutePlan(request_id='1234', callback_url='http://someurl',
                              status_callback_url='http://somestatusurl')
        routeplan.orders = []
        with pytest.raises(ValueError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.orders' must have at least 1 element".format(cls_name)
        assert err_msg == str(excinfo.value)

        routeplan = RoutePlan(request_id='1234', callback_url='http://someurl',
                              status_callback_url='http://somestatusurl')
        routeplan.orders = [3]
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.orders' must contain elements of type Order".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_drivers(self, cls_name, orders, routeplan):
        routeplan.orders = list(orders)
        routeplan.drivers = 3
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'drivers', (list, tuple), int)
        assert err_msg == str(excinfo.value)

        routeplan.orders = list(orders)
        routeplan.drivers = []
        with pytest.raises(ValueError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.drivers' must have at least 1 element".format(cls_name)
        assert err_msg == str(excinfo.value)

        routeplan.orders = list(orders)
        routeplan.drivers = [3]
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.drivers' must contain elements of type Driver".\
            format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_orders_scheduled_driver(self, orders, drivers, routeplan):
        drivers = list(drivers)
        # pop rantanplan from the list
        drivers.pop()
        routeplan.orders = list(orders)
        routeplan.drivers = drivers

        with pytest.raises(OptimoValidationError) as excinfo:
            routeplan.validate()
        err_msg = "SchedulingInfo defines driver with id: 'rantanplan' that " \
                  "is not present in 'drivers' list"
        assert err_msg == str(excinfo.value)

    def test_orders_assigned_to(self, orders, drivers, routeplan):
        order = Order(id='new_order', lat=3, lng=4, duration=5,
                      assigned_to="New Driver")
        routeplan.orders = list(orders)
        # add the new order with the new and unknown driver
        routeplan.orders.append(order)
        routeplan.drivers = list(drivers)
        with pytest.raises(OptimoValidationError) as excinfo:
            routeplan.validate()
        err_msg = ("The order with id: 'new_order' is assigned to driver with "
                   "id: 'New Driver' that is not present in 'drivers' list")
        assert err_msg == str(excinfo.value)

    def test_no_load_capacities(self, cls_name, orders, drivers, routeplan):
        routeplan.orders = list(orders)
        routeplan.drivers = list(drivers)
        routeplan.no_load_capacities = 'HA'
        with pytest.raises(TypeError) as excinfo:
            routeplan.validate()
        err_msg = TYPE_ERR_MSG.format(cls_name, 'no_load_capacities', (int, long), str)
        assert err_msg == str(excinfo.value)

        routeplan.orders = list(orders)
        routeplan.drivers = list(drivers)
        routeplan.no_load_capacities = 5
        with pytest.raises(ValueError) as excinfo:
            routeplan.validate()
        err_msg = "'{}.no_load_capacities' must be between 0-4".format(cls_name)
        assert err_msg == str(excinfo.value)

    def test_is_valid(self, orders, drivers, routeplan):
        routeplan.orders = list(orders)
        routeplan.drivers = list(drivers)
        routeplan.no_load_capacities = 3
        assert routeplan.validate() is None
        assert jsonify(routeplan) == (
            '{"noLoadCapacities": 3, "statusCallback": "http://somestatusurl",'
            ' "drivers": [{"endLon": 5, "skills": ["calm", "angry"], "endLat":'
            ' 4, "startLat": 3, "workShifts": [{"workTimeFrom": '
            '"2014-12-05T08:00", "workTimeTo": "2014-12-05T08:00"}], '
            '"startLon": 4, "id": "Tom & Jerry"}, {"endLon": 5, "skills": '
            '["pirate", "ninja"], "endLat": 4, "startLat": 3, "workShifts": '
            '[{"workTimeFrom": "2014-12-05T08:00", "workTimeTo": '
            '"2014-12-05T08:00"}], "startLon": 4, "id": "Sam & Max"}, '
            '{"endLon": 5, "skills": ["woofing", "barking"], "endLat": 4, '
            '"startLat": 3, "workShifts": [{"workTimeFrom": "2014-12-05T08:00",'
            ' "workTimeTo": "2014-12-05T08:00"}], "startLon": 4, "id": '
            '"rantanplan"}], "callback": "http://someurl", "requestId": "1234",'
            ' "orders": [{"assignedTo": "Tom & Jerry", "skills": ["handy",'
            ' "quiet"], "tw": {"timeFrom": "2014-12-05T08:00", '
            '"timeTo": "2014-12-05T08:00"}, "lon": 6.1, "priority": "M", '
            '"duration": 7, "lat": 5.2, "schedulingInfo": {"scheduledAt": '
            '"2014-12-05T08:00", "locked": false, "scheduledDriver": '
            '"rantanplan"}, "id": "3"}, {"assignedTo": "Sam & Max", "skills": '
            '["barista", "terrorista"], "tw": {"timeFrom": "2014-12-05T08:00", '
            '"timeTo": "2014-12-05T08:00"}, "lon": 6.1, "priority": "M", '
            '"duration": 7, "lat": 5.2, "schedulingInfo": {"scheduledAt": '
            '"2014-12-05T08:00", "locked": false, "scheduledDriver": '
            '"rantanplan"}, "id": "4"}]}'
        )
        assert RoutePlanValidator.validate(dictify(routeplan)) is None

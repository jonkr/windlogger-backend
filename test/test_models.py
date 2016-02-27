#!/usr/bin/env python
# -*- coding: utf-8 -*-

from test.base import TestBase

from models import Sample, Sensor

class TestSensorSample(TestBase):

    def test_make_sample(self):
        s = Sensor(id=1, name=u'Dalarö', longitude=1.0, latitude=2.0,
                           type='viva')
        s.store()
        ss = Sample(sensor_id=1, date_reported=self.now, type='wind_speed', data=2.1)
        ss.store()
        samples = Sample.get_last(id=1)
        assert len(samples) == 1
        assert samples[0].data == 2.1


class TestSensor(TestBase):

    def test_make_sensor(self):
        s = Sensor(id=1, name=u'Dalarö', longitude=1.0, latitude=2.0,
                           type='viva')
        s.store()
        sensors = Sensor.get_all()
        assert len(sensors) == 1
        assert sensors[0].id == 1




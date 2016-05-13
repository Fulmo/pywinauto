"""Tests for CalendarWrapper"""
import datetime
import os
import sys
import unittest

sys.path.append(".")
from pywinauto import win32structures
from pywinauto import win32defines
from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python

mfc_samples_folder = os.path.join(
   os.path.dirname(__file__), r"..\..\apps\MFC_samples")
if is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

class CalendarWrapperTests(unittest.TestCase):

    """Unit tests for the CalendarWrapperTests class"""
    NO_HOLIDAYS_IN_MONTH = 0

    CALENDARBK_WIDTH_COEFF = 9
    CALENDARBK_HEIGHT_OFFSET = 112
    TITLEBK_WIDTH_COEFF = 2
    TITLEBK_HEIGHT_COEFF = 26.67

    def setUp(self):
        """Start the application set some data and ensure the application
        is in the state we want it."""
        self.app = Application().start(os.path.join(mfc_samples_folder, u"CmnCtrl1.exe"))

        self.dlg = self.app.Common_Controls_Sample
        self.dlg.TabControl.Select(4)
        self.calendar = self.app.Common_Controls_Sample.CalendarWrapper

        rect = self.app['Common Controls Sample']['Calendar'].Rectangle()
        self.width = rect.width()
        self.height = rect.height()

    def tearDown(self):
        """Close the application after tests"""
        # close the application
        self.dlg.type_keys("%{F4}")

    def test_can_get_current_date_from_calendar(self):
        date = self.calendar.get_current_date()
        self.assert_system_time_is_equal_to_current_date_time(date,datetime.date.today())

    def test_should_throw_runtime_error_when_try_to_get_current_date_from_calendar_if_calendar_state_is_multiselect(self):
        self._set_calendar_state_into_multiselect()
        self.assertRaises(RuntimeError, self.calendar.get_current_date)

    def test_can_set_current_date_in_calendar(self):
        self.calendar.set_current_date(2016, 4, 3, 13)
        self.assert_system_time_is_equal_to_current_date_time(self.calendar.get_current_date(), datetime.date(2016, 4, 13)) 

    def test_should_throw_runtime_error_when_try_to_set_invalid_date(self):
        self.assertRaises(RuntimeError, self.calendar.set_current_date, -2016, -4, -3, -13)

    def test_can_get_calendar_border(self):
        width = self.calendar.get_border()
        self.assertEqual(width, 4)

    def test_can_set_calendar_border(self):
        self.calendar.set_border(6)
        self.assertEqual(self.calendar.get_border(), 6)

    def test_can_get_calendars_count(self):
        count = self.calendar.count()
        self.assertEqual(count, 1)

    def test_can_get_calendars_view(self):
        view = self.calendar.get_view()
        self.assertEqual(view, 0)

    def test_should_throw_runtime_error_when_try_to_set_invalid_view(self):
        self.assertRaises(RuntimeError, self.calendar.set_view, -1)

    def test_can_set_calendars_view_into_month(self):
        self.calendar.set_view(win32defines.MCMV_MONTH)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_MONTH)

    def test_can_set_calendars_view_into_years(self):
        self.calendar.set_view(win32defines.MCMV_YEAR)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_YEAR)

    def test_can_set_calendars_view_into_decade(self):
        self.calendar.set_view(win32defines.MCMV_DECADE)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_DECADE)

    def test_can_set_calendars_view_into_century(self):
        self.calendar.set_view(win32defines.MCMV_CENTURY)
        self.assertEqual(self.calendar.get_view(), win32defines.MCMV_CENTURY)

    def test_can_set_day_state(self):
        month_states = [self.NO_HOLIDAYS_IN_MONTH, self.NO_HOLIDAYS_IN_MONTH, self.NO_HOLIDAYS_IN_MONTH]
        self._set_calendar_state_to_display_day_states()

        res = self.calendar.set_day_states(month_states)

        self.assertNotEquals(0, res)

    def test_cant_set_day_state_passing_one_month_state(self):
        month_states = [self.NO_HOLIDAYS_IN_MONTH]
        self._set_calendar_state_to_display_day_states()
        self.assertRaises(RuntimeError, self.calendar.set_day_states, month_states)

    def test_can_minimize_rectangle(self):
        expected_rect = self._get_expected_minimized_rectangle()
        rect = self.calendar.calc_min_rectangle(expected_rect.left + 100, expected_rect.top + 100,
                                                expected_rect.right + 100, expected_rect.bottom + 100)
        self.assertEquals(expected_rect, rect)

    def test_can_minimize_rectangle_handle_less_than_zero_values(self):
        expected_rect = self._get_expected_minimized_rectangle()
        rect = self.calendar.calc_min_rectangle(-1, -1, -1, -1)
        self.assertEquals(expected_rect, rect)

    def test_can_determine_calendar_is_hit(self):
        x = int(self.width / self.CALENDARBK_WIDTH_COEFF)
        y = int(self.height - self.CALENDARBK_HEIGHT_OFFSET)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDAR, res)

    def test_can_determine_calendar_background_is_hit(self):
        x = int(self.width / self.CALENDARBK_WIDTH_COEFF)
        y = int(self.height - self.CALENDARBK_HEIGHT_OFFSET)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARBK, res)

    def test_can_determine_date_is_hit(self):
        x = int(self.width / 1.14)
        y = int(self.height / 1.33)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARDATE, res)

    def test_can_determine_next_month_date_is_hit(self):
        x = int(self.width / 1.14)
        y = int(self.height / 1.23)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARDATENEXT, res)

    def test_can_determine_prev_month_date_is_hit(self):
        x = int(self.width / 16)
        y = int(self.height / 2.67)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARDATEPREV, res)

    def test_can_determine_nothing_is_hit(self):
        res = self.calendar.hit_test(0, 0)
        self.assertEquals(win32defines.MCHT_NOWHERE, res)

    def test_can_determine_top_left_title_corner_is_hit(self):
        x = int(self.width / 16)
        y = int(self.height / 16)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_TITLEBTNPREV, res)

    def test_can_determine_title_is_hit(self):
        x = int(self.width / self.TITLEBK_WIDTH_COEFF)
        y = int(self.height / self.TITLEBK_HEIGHT_COEFF)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_TITLE, res)

    def test_can_determine_title_background_is_hit(self):
        x = int(self.width / self.TITLEBK_WIDTH_COEFF)
        y = int(self.height / self.TITLEBK_HEIGHT_COEFF)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_TITLEBK, res)

    def test_can_determine_top_right_title_corner_is_hit(self):
        x = int(self.width / 1.07)
        y = int(self.height / 8)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_TITLEBTNNEXT, res)

    # TODO: test_can_determine_today_link_is_hit fails in CI with strange res = 1048576.
    # There is no such value for MCHT_* defines.
    # def test_can_determine_today_link_is_hit(self):
    #     x = int(self.width / 1.25)
    #     y = int(self.height / 1.14)
    #
    #     res = self.calendar.test_hit(x, y)
    #
    #     self.assertEquals(win32defines.MCHT_TODAYLINK, res)

    def test_can_determine_day_abbreviation_is_hit(self):
        x = int(self.width / 5.33)
        y = int(self.height / 4)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARDAY, res)

    def test_can_determine_week_number_is_hit(self):
        self._set_calendar_state_to_display_week_numbers()
        x = int(self.width / 13.5)
        y = int(self.height / 1.7)

        res = self.calendar.hit_test(x, y)

        self.assertEquals(win32defines.MCHT_CALENDARWEEKNUM, res)

    def test_should_throw_runtime_error_when_try_to_set_invalid_type_of_calendar(self):
        self.assertRaises(ValueError, self.calendar.set_id, 'Aloha!')

    def test_should_get_valid_type_of_calendar(self):
        self.assertEqual(self.calendar.get_id(), 0)

    def test_should_throw_runtime_error_when_try_to_set_invalid_type_of_place_for_color(self):
        self.assertRaises(ValueError, self.calendar.set_color, 'Aloha!', 0, 0, 0)

    # TODO create tests for get_color in future
    '''
    def test_return_zero_when_color_not_set_early(self):
        self.assertEqual(self.calendar.get_color('text'), 0)
    '''

    '''
    def test_should_get_valid_calendar_color(self):
        self.calendar.set_color('text', 5, 5, 5)
        self.assertEqual(self.calendar.get_color('text'), 328965)
    '''

    def test_return_error_about_color(self):
        self.assertRaises(RuntimeError, self.calendar.set_color, 'background', -1, -1, -1)

    def test_return_error_when_color_hire_then_255(self):
        self.assertRaises(RuntimeError, self.calendar.set_color, 'background', 600, 600, 600)

    def test_can_get_today(self):
        """Test getting the control's today field"""
        date = self.calendar.get_today()
        self.assert_system_time_is_equal_to_current_date_time(date, datetime.date.today())

    def test_can_set_today(self):
        """Test setting up the control's today field"""
        self.calendar.set_today(2016, 5, 1)
        self.assert_system_time_is_equal_to_current_date_time(self.calendar.get_today(),
                                                              datetime.date(2016, 5, 1))

    def test_can_set_and_get_first_day_of_week(self):
        """Test can set and get first day of the week"""
        self.calendar.set_first_weekday(4)
        self.assertEqual((True,4), self.calendar.get_first_weekday())

    def assert_system_time_is_equal_to_current_date_time(self,systemTime, now):
        self.assertEqual(systemTime.wYear, now.year)
        self.assertEqual(systemTime.wMonth, now.month)
        self.assertEqual(systemTime.wDay, now.day)

    def _get_expected_minimized_rectangle(self):
        expected_rect = win32structures.RECT()
        expected_rect.left = 0
        expected_rect.top = 0
        expected_rect.right = self.width
        expected_rect.bottom = self.height
        return expected_rect

    def _set_calendar_state_to_display_day_states(self):
        self.app['Common Controls Sample']['MCS_DAYSTATE'].Click()


    def _set_calendar_state_to_display_week_numbers(self):
        self.app['Common Controls Sample']['MCS_WEEKNUMBERS'].Click()


    def _set_calendar_state_into_multiselect(self):
        self.app['Common Controls Sample']['MCS_MULTISELECT'].Click()

if __name__ == "__main__":
    unittest.main()

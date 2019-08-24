from calanderific_holiday_api import *


class HolidayFeatureExtractor:
    holiday_vicinity_dict: dict = None
    data_loaded: bool = False

    DATA_PATH = '../Data/HolidayData_NY_2014-2019.bin'

    HOLIDAY_TYPES = [HolidayType.NationalHoliday, HolidayType.Christian]

    @classmethod
    def load_data(cls):

        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if module == "__main__":
                    module = 'calanderific_holiday_api'
                return super().find_class(module, name)

        with open(cls.DATA_PATH, 'rb') as f:
            holiday_data = CustomUnpickler(f).load()

        min_date = min(holiday_data.keys)
        max_date = max(holiday_data.keys)

        cls.holiday_vicinity_dict = {}
        for ht in cls.HOLIDAY_TYPES:
            cls.holiday_vicinity_dict[ht] = \
                cls.get_holiday_vicinity_status_per_date(holiday_data, ht, min_date, max_date)

    @classmethod
    def get_holiday_vicinity_status_per_date(cls, holiday_data, holiday_type, start_date,
                                             end_date, vicinity=3):
        remaining_forward_vicinity = 0

        ret = {}
        date = start_date
        while date <= end_date:
            has_relevant_holiday = False
            if date in holiday_data:
                for h_name in holiday_data[date]:
                    for t in holiday_data[date][h_name].types:
                        if t == holiday_type:
                            has_relevant_holiday = True
                            break

            if has_relevant_holiday:
                # Occurs when not in another holiday's vicinity
                if remaining_forward_vicinity == 0:
                    # remaining_backward_vicinity = vicinity
                    for i in range(1, vicinity + 1):
                        ret[date - timedelta(days=i)] = True
                remaining_forward_vicinity = vicinity + 1

            ret[date] = remaining_forward_vicinity > 0
            remaining_forward_vicinity -= 1
            date += timedelta(days=1)

        return ret

    @classmethod
    def get_feature_dict(cls, date_):

        date_ = date.fromisoformat(date_)

        ret = {}
        for ht in cls.HOLIDAY_TYPES:
            ret[ht.value.upper().replace(' ', '_')] = date_ in cls.holiday_vicinity_dict[ht] \
                                                      and cls.holiday_vicinity_dict[ht][date_]

def get_holiday_features_dict(date):
    """

    :param date: The content of the column 'FL_DATE'
    :return: rtn_dict: {NATIONAL_HOLIDAY: bool, CHRISTIAN: bool}
    """
    return HolidayFeatureExtractor.get_feature_dict(date)


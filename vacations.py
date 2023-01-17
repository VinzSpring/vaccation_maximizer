from datetime import timedelta
from datetime import datetime
from holidays import HolidayBase


class TimeBin:
    def __init__(self, start_date, end_date, is_holiday):
        self.is_holiday = is_holiday
        self.start_date = start_date
        self.end_date = end_date

    def n_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"TimeBin({self.start_date}, {self.end_date}, {self.is_holiday}, {self.n_days()})"


class VacationCandidate:
    def __init__(self, start, end, n_days, n_holidays, ratio):
        self.start = start
        self.end = end
        self.n_days = n_days
        self.n_holidays = n_holidays
        self.ratio = ratio

    def from_bins(bins):
        n_days = sum([bin.n_days() for bin in bins])
        n_holidays = sum([bin.n_days() for bin in bins if bin.is_holiday])
        ratio = n_holidays / n_days
        return VacationCandidate(bins[0].start_date, bins[-1].end_date, n_days, n_holidays, ratio)

    def __str__(self):
        return f"from {self.start} to {self.end} ({self.n_days} days, {self.n_holidays} holidays, {self.ratio} ratio)"

    def __repr__(self):
        return self.__str__()


def date_range(start, end) -> list:
    """return list of dates between start and end"""
    delta = timedelta(days=1)
    while start <= end:
        yield start
        start += delta


def to_bins(start, end, holidays: HolidayBase, free_weekdays=[5, 6]):
    """return list of time bins, separating between weekdays and holidays (free weekdays are considered holidays too)"""
    bins = []
    current_bin = None
    for day in date_range(start, end):
        is_holiday = day.weekday() in free_weekdays or day in holidays
        if current_bin is None:
            current_bin = TimeBin(day, day, is_holiday)
        elif current_bin.is_holiday != is_holiday:
            bins.append(current_bin)
            current_bin = TimeBin(day, day, is_holiday)
        else:
            current_bin.end_date = day
    if current_bin is not None:
        bins.append(current_bin)
    return bins


def get_best_sublists(bins, max_len, min_len):
    """returns the best lists of bins where the ratio of holidays to weekdays is as high as possible. the total sum of days must be between min_len and max_len"""
    best_lists = []
    current_list = []
    best_ratio = 0
    for i in range(len(bins)):
        for j in range(i, len(bins)):
            current_list = bins[i:j+1]
            n_days = sum([bin.n_days() for bin in current_list])
            if n_days > max_len:
                break
            if n_days >= min_len:
                n_holidays = sum([bin.n_days() for bin in current_list if bin.is_holiday])
                ratio = n_holidays / n_days
                if ratio > best_ratio:
                    best_lists = [current_list]
                    best_ratio = ratio
                elif ratio > best_ratio / 2:
                    best_lists.append(current_list)
    sorted_lists = sorted(best_lists, key=lambda x: sum(
        [bin.n_days() for bin in x if bin.is_holiday]) / sum([bin.n_days() for bin in x]))
    return sorted_lists


def choose_optimal_candidates(candidates, max_non_holiday_days):
    """returns the best candidates which in sum could cover the most days but do not not contain (in total) more than max_non_holiday_days"""
    candidates.sort(key=lambda x: x.ratio, reverse=True)
    best_candidates = []
    current_non_holiday_days = 0
    for candidate in candidates:
        if current_non_holiday_days + candidate.n_days - candidate.n_holidays > max_non_holiday_days:
            break
        best_candidates.append(candidate)
        current_non_holiday_days += candidate.n_days - candidate.n_holidays
    return best_candidates


def get_vacation_recommendation(start, end, holidays: HolidayBase, max_len, min_len, max_non_holiday_days):
    bins = to_bins(start, end, holidays)
    best_lists = get_best_sublists(bins, max_len, min_len)
    candidates = [VacationCandidate.from_bins(x) for x in best_lists]
    return choose_optimal_candidates(candidates, max_non_holiday_days)

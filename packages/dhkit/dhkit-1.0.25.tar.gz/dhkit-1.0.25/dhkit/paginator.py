# coding:utf8

"""
Created on 2014-09-30

@author: tufei
@description: 实现分页功能
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import collections


class PaginationError(Exception):
    """
    """


class Paginator(object):

    def __init__(self, per_page, total):
        self.per_page = int(per_page)
        self.total = int(total)
        assert (self.total >= 0)
        self.num_pages = (self.total / self.per_page + ((self.total % self.per_page > 0) and 1 or 0))

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PaginationError('That page number is not an integer')
        if number < 1:
            raise PaginationError('That page number is less than 1')
        if number > self.num_pages:
            if number == 1:
                pass
            else:
                raise PaginationError('That page contains no results')
        return number

    def page(self, page_number, objs):
        number = self.validate_number(page_number)
        if not isinstance(objs, (list, tuple)):
            raise TypeError

        objs_len = len(objs)
        if page_number == self.num_pages:
            if objs_len > self.per_page:
                raise PaginationError("objs length %s erro for page_number: %s" % (objs_len, page_number))
        else:
            if objs_len != self.per_page:
                raise PaginationError("objs length %s erro for page_number: %s" % (objs_len, page_number))
        return Page(number, objs, self)


class Page(collections.Sequence):

    def __init__(self, number, objs, paginator):
        self.number = number
        self.objs = objs
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def __len__(self):
        return len(self.objs)

    def __getitem__(self, index):
        if not isinstance(index, (slice, int, long)):
            raise TypeError
        return self.objs[index]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.total == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.total
        return self.number * self.paginator.per_page

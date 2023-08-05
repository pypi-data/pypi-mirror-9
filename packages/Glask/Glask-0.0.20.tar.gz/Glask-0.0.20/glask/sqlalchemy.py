from __future__ import unicode_literals, print_function, absolute_import, \
    division


class Navigation(object):
    def __init__(self, current, pages, previous, next):
        self.next = next
        self.previous = previous
        self.pages = pages
        self.current = current
        self.has_previous = self.previous < self.pages[0]
        self.has_next = self.next > self.pages[-1]


class Pagination(object):
    def __init__(self, query, page=0, per_page=10, navigation_length=10):
        self.total = query.count()
        self.final_page = self.total // 10
        self.page = max(min(page, self.final_page), 0)
        self.items = query[self.page * per_page:(self.page + 1) * per_page]

        start_page = (page - page % navigation_length)
        last_page = min(start_page + navigation_length - 1, self.final_page)
        next_page = min(start_page + navigation_length, self.final_page)
        self.navigation = Navigation(
            current=self.page, pages=range(start_page, last_page + 1),
            previous=max(start_page - 1, 0), next=next_page
        )

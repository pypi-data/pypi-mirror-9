import re

from collections import defaultdict
from datetime import datetime, timedelta
from optparse import make_option

from user_agents import parse

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from djanalytics import models
from django.db.models.aggregates import Sum, Count

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '-s', '--start', type='string',
            help='Beginning date for request events. If not provided, '
                 'request events from the beginning of time will be '
                 'selected.'
        ),
        make_option(
            '-e', '--end', type='string',
            help='End date for request events. If not provided, '
                 'up to the most recent request event will be selected.'
        ),
        make_option(
            '-a', '--max-age', type='int', dest='max_age', default=30,
            help='Max number of days in the past to look for Visit and '
                 'PageVisit objects. Default is 30.'
        )
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.device_cache = {}
        self.device_type_cache = {}
        self.visitor_cache = {}
        self.visit_cache = {}
        self.page_cache = {}
        self.page_pattern_cache = {}
        self.web_property_cache = {}

    def handle(self, start=None, end=None, max_age=30, **options):
        self.max_age = max_age

        self.create_page_visits(start, end)
        self.calculate_page_durations()
        self.collect_visit_data()

    def create_page_visits(self, start, end):
        domains = list(models.Domain.objects.values_list('name', flat=True).distinct())
        query_dict = {
            'pagevisit': None,
            'domain__in': domains,
        }
        if start:
            start = parse_date(start)
            query_dict['created__gte'] = start
        if end:
            end = parse_date(end)
            query_dict['created__lte'] = end

        query = models.RequestEvent.objects.filter(
            **query_dict
        ).order_by('tracking_user_id', 'created')
        total_events = query.count()
        self.stdout.write(
            'Processing %s RequestEvents - Start: %s\tEnd: %s\n' % (
                total_events,
                start.strftime('%m/%d/%Y') if start else 'None',
                end.strftime('%m/%d/%Y') if end else 'None'
            )
        )
        for cnt, request_event in enumerate(query):
            if cnt % 1000 == 0:
                self.stdout.write('Processed %s of %s\n' % (cnt, total_events))
            device = self.device_cache.get(request_event.user_agent)
            if not device:
                user_agent = parse(request_event.user_agent)
                device, created = models.Device.objects.get_or_create(
                    user_agent=request_event.user_agent,
                    defaults={
                        'screen_width': request_event.screen_width,
                        'screen_height': request_event.screen_height,
                        'os': user_agent.os.family,
                        'os_version': user_agent.os.version_string,
                        'browser': user_agent.browser.family,
                        'browser_version': user_agent.browser.version_string,
                        'device': user_agent.device.family,
                        'device_type': self._get_device_type(user_agent),
                    }
                )
                self.device_cache[request_event.user_agent] = device
            visitor = self.visitor_cache.get(request_event.tracking_user_id)
            if not visitor:
                visitor, _created = models.Visitor.objects.get_or_create(
                    uuid=request_event.tracking_user_id,
                )
                self.visitor_cache[request_event.tracking_user_id] = visitor
            visitor.clients.add(request_event.client)
            page_key = (request_event.path, request_event.client)
            page = self.page_cache.get(page_key)
            if not page:
                page_type = None
                page_patterns = self.page_pattern_cache.get(request_event.client)
                if page_patterns is None:
                    page_patterns = request_event.client.pagepattern_set.all()
                    self.page_pattern_cache[request_event.client] = page_patterns
                for page_pattern in page_patterns:
                    if re.match(page_pattern.pattern, request_event.path, re.IGNORECASE):
                        page_type = page_pattern.page_type
                        break
                page, created = models.Page.objects.get_or_create(
                    path=request_event.path,
                    client=request_event.client,
                    defaults={"page_type": page_type}
                )
                self.page_cache[page_key] = page
            web_property = self.web_property_cache.get(request_event.domain)
            if not web_property:
                try:
                    web_property = models.WebProperty.objects.get(domain__name=request_event.domain)
                except models.WebProperty.DoesNotExist:
                    self.stdout.write(
                        'No WebProperty found for domain: %s - skipping' % request_event.domain
                    )
                    continue
                except models.WebProperty.MultipleObjectsReturned:
                    self.stdout.write(
                        'Multiple WebProperties found for domain: %s - skipping' % (
                            request_event.domain
                        )
                    )
                    continue
                else:
                    self.web_property_cache[request_event.domain] = web_property
            visit = self.visit_cache.get(request_event.tracking_key)
            if not visit:
                visit, _created = models.Visit.objects.get_or_create(
                    uuid=request_event.tracking_key,
                    visitor=visitor,
                    defaults={
                        'first_page': page,
                        'device': device,
                        'visit_date': request_event.created.date(),
                        'web_property': web_property,
                    },
                )
                self.visit_cache[request_event.tracking_key] = visit

            models.PageVisit.objects.create(
                page=page,
                visit=visit,
                request_event=request_event
            )

    def calculate_page_durations(self):
        # finding all page visits with no duration
        # from the last 'max_age' days
        query = models.PageVisit.objects.filter(
            duration=None,
            request_event__created__gte=datetime.now() - timedelta(
                days=self.max_age
            ),
        ).distinct().order_by('visit__uuid')
        all_visits = list(
            query.values_list(
                'request_event__tracking_key', flat=True
            ).distinct()
        )
        total_visits = len(all_visits)
        start_idx = 0
        subset = 100000 if total_visits > 100000 else total_visits
        while start_idx < total_visits:
            self.stdout.write('\n')
            self.stdout.write('Processing %s to %s of %s total '
                'page visits for duration\n' % (
                    start_idx,
                    start_idx + subset
                        if start_idx + subset < total_visits else total_visits,
                    total_visits
                )
            )
            tracking_keys = all_visits[start_idx: start_idx+subset]
            start_idx += subset
            # finding sessions with more than one request event
            events = list(
                models.RequestEvent.objects.filter(
                    tracking_key__in=tracking_keys
                ).values(
                    'tracking_key'
                ).annotate(
                    Count('tracking_key')
                ).order_by().filter(
                    tracking_key__count__gt=1
                ).values_list('tracking_key', flat=True).distinct()
            )
            # limit the page visits to just those with sessions that
            # have more than one request event
            subquery = query.filter(request_event__tracking_key__in=events)
            total_page_visits = subquery.count()
            self.stdout.write('Processing %s page visits for durations\n' % total_page_visits)
            for cnt, page_visit in enumerate(subquery):
                if cnt % 1000 == 0:
                    self.stdout.write(
                        'Processed %s of %s page visits\n' % (cnt, total_page_visits)
                    )
                try:
                    # get the next chronological request event
                    next_event = models.RequestEvent.objects.filter(
                        tracking_key=page_visit.request_event.tracking_key,
                        created__gt=page_visit.request_event.created
                    ).earliest()
                    elapsed_delta = next_event.created - page_visit.request_event.created
                    page_visit.duration = round(elapsed_delta.total_seconds())
                    page_visit.save()
                except models.RequestEvent.DoesNotExist:
                    # nothing newer than the current PageVisit
                    pass

    def collect_visit_data(self):
        # Visit data
        self.page_pattern_cache = defaultdict(list)
        query = models.Visit.objects.filter(
            visit_date__gte=(datetime.now() - timedelta(days=self.max_age))
        ).distinct().annotate(calc_duration=Sum('pagevisit__duration'))
        total_visits = query.count()
        self.stdout.write('\n')
        self.stdout.write('Processing %s visits\n' % total_visits)
        for cnt, visit in enumerate(query):
            if cnt % 1000 == 0:
                self.stdout.write('Processed %s of %s visits\n' % (cnt, total_visits))
            changed = False
            if visit.last_page != visit.pagevisit_set.latest():
                changed = True
                visit.last_page = visit.pagevisit_set.latest().page
            order_ids = []
            conversion_count = 0
            funnel_found = False
            for page_visit in visit.pagevisit_set.filter(
                page__page_type__code__in=(
                    models.PageType.CONVERSION,
                    models.PageType.FUNNEL
                )
            ).order_by('request_event__created'):
                page_patterns = self.page_pattern_cache.get(page_visit.page.client)
                if page_patterns is None:
                    page_patterns = defaultdict(list)
                    for pattern in page_visit.page.client.pagepattern_set.filter(
                        page_type__code__in=(
                            models.PageType.CONVERSION,
                            models.PageType.FUNNEL
                        )
                    ):
                        page_patterns[pattern.page_type.code].append(
                            re.compile(pattern.pattern)
                        )
                        self.page_pattern_cache[page_visit.page.client] = page_patterns
                # in order to count a conversion, the visitor has to have hit
                # at least one funnel page
                for pattern in page_patterns[models.PageType.FUNNEL]:
                    if pattern.match(page_visit.page.path):
                        funnel_found = True
                        break
                for pattern in page_patterns[models.PageType.CONVERSION]:
                    m = pattern.match(page_visit.page.path)
                    if m and len(m.groups()) > 0 and funnel_found:
                        order_ids.append(m.group(1))
                        funnel_found = False
                        break
                conversion_count = len(set(order_ids))
            if visit.conversion_count != conversion_count:
                changed = True
                visit.conversion_count = conversion_count
            if visit.duration != visit.calc_duration:
                changed = True
                visit.duration = visit.calc_duration
            if changed:
                visit.save()

    def _get_device_type(self, user_agent):
        code = models.DeviceType.UNKNOWN
        if user_agent.is_mobile:
            code = models.DeviceType.MOBILE
        elif user_agent.is_tablet:
            code = models.DeviceType.TABLET
        elif user_agent.is_pc:
            code = models.DeviceType.DESKTOP
        elif user_agent.is_bot:
            code = models.DeviceType.BOT
        device_type = self.device_type_cache.get(code)
        if not device_type:
            device_type, _created = models.DeviceType.objects.get_or_create(
                code=code,
                defaults={'name': code.capitalize()}
            )
            self.device_type_cache[code] = device_type
        return device_type

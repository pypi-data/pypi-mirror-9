import codecs
import simplejson as json
import os
import utils

from collections import defaultdict
from export import Export
#from mixpanel import *  ###Utilize forked mixpanel lib until mixpanel-python catches up###
from tracker import *


class Services(object):
    """
    Service related capabilities to massage data
    """

    def __init__(self, token, api_key = None, api_secret = None, project_name = None):
        """
        Creates a new Services object which will access and send data from and to Mixpanel
        """
        self.token = token
        self.api_key = api_key
        self.api_secret = api_secret
        self.name = project_name if project_name else token
        self.api = Export(api_key, api_secret)
        self.tracker = Mixpanel(self.token, BufferedConsumer())

    def printer(self):
        return self.api_key

    def raw_increment(self, event_json_list, event_name, event_property = None, event_property_value = None, people_property = None):
        """
        comb through raw data to create an incremented People property
        """
        increments = defaultdict(int)
        for event in event_json_list:
            if event.get('event') == event_name:
                distinct = event.get('properties', {}).get('distinct_id', None)

                if not distinct:
                    continue

                if event_property and event_property_value:
                    if event.get('properties', {}).get(event_property, None) == event_property_value:
                        increments[str(distinct)] += 1
                else:
                    increments[str(distinct)] += 1

        for user, count in increments.iteritems():
            self.tracker.people_increment(user, {people_property: count}, {'$ignore_time': True})

        self.tracker._consumer.flush()

        return len(increments)

    def raw(self, from_date, to_date, events=None, where=None):
        """
        Pull and return raw data
        """
        if not (self.token and self.api_key and self.api_secret):
            print "API Credentials required: token, api_key, api_secret"
            exit()

        params = {'from_date' : from_date, 'to_date' : to_date}
        if where:
            params.update({'where' : where})
        if events and isinstance(events, list):
            params.update({'event' : events})

        return self.api.request(['export'], params, output_file=utils.file_path(self.name, 'export-' + str(int(time.time())) + '.txt'))

    def raw_to_s3(self):
        """
        pull and send raw data to an s3 bucket
        """
        pass

    def formatted(self):
        """
        Access formatted reports through api
        """
        pass

    def people_export(self, selector = None):
        """
        Grab users from a project
        """
        parameters = {}
        if selector:
            parameters['selector'] = selector

        response = self.api.request(['engage'], parameters)

        parameters.update({
                'session_id' : response['session_id'],
                'page' :0
                })

        global_total = response.get('total')

        print "Here are the # of people %d" % global_total

        fname = utils.file_path(self.name, 'people' + "-" + str(int(time.time())) + ".txt")
        has_results = True
        total = 0
        print fname
        f = codecs.open(fname, 'w', encoding='utf-8')
        while has_results:
            responser = response['results']
            total += len(responser)
            has_results = total < global_total
            for data in responser:
                    f.write(json.dumps(data)+'\n')
            print "%d / %d" % (total,global_total)

            if has_results:
                parameters['page'] += 1
                response = self.api.request(['engage'], parameters)

        return fname

    def people_distincts(self, filename):
        """
        Grab a list of $distinct_id s from a Mixpanel People export
        """
        people = []
        for person in utils.export_parse_pager(filename):
            people.append(person['$distinct_id'])
        print "This many people", len(people)
        people = list(set(people))
        print "done finding uniques", len(people)
        return people

    def people_bulk_update(self, message, distincts_list):
        """
        Send a generalized update to profiles
        """

        for user in distincts_list:
            temp = {'$distinct_id' : user}
            temp.update(message)
            self.tracker.people_update(temp)

        self.tracker._consumer.flush()

        return len(distincts_list)

    def safe_zip(self):
        utils.safe_zip(self.name, self.api_secret)

    def csv_write(self, object_list, filename = None):
        fname = utils.file_path(self.name, (filename if filename else '') + "-" + str(int(time.time())) + ".csv")
        return utils.csv_write(object_list, fname)

    def orphan_finder(self):
        """
        Finds and returns all orphan profiles
        """
        users = self.people_export()
        set_orphan = {'$set' : { 'Orphan' : True }, '$ignore_alias' : 'true', '$ignore_time' : 'true'}
        unset_orphan = {'$unset' : ['Orphan'], '$ignore_time' : 'true'}
        people_count = 0
        people = []
        for person_generator in utils.export_parse_pager(users):
            people.append(person_generator['$distinct_id'])
            if len(people) >= 50:
                people_count += len(people)
                print 'Updated %s people' % people_count
                self.people_bulk_update(set_orphan, people)
                self.people_bulk_update(unset_orphan, people)
                people = []
        print 'Last batch of %s people' % len(people)
        self.people_bulk_update(set_orphan, people)
        self.people_bulk_update(unset_orphan, people)
        orphans = self.people_export('(defined (properties["Orphan"]))') 
        return orphans

class Analysis(object):
    """
    Diagnosis of trouble and investigation of current data
    """

    def __init__(self, api_key, api_secret):
        """
        Create a new object to grab and analyze Mixpanel data
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def funnel_doctor(self):
        pass

    def gap_analysis(self):
        pass







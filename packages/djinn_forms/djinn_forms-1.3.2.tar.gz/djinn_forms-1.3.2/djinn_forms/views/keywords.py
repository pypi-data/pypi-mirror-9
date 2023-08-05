import json
from django.http import HttpResponse
from django.views.generic import View
from haystack.query import SearchQuerySet


class Keywords(View):

    """ Perform a keyword search on the indexed keywords, and return a list of
    the found keywords, with their frequency """

    def get(self, request):

        kw = self.request.GET.get("term")

        sqs = SearchQuerySet().filter(
            keywords__startswith=kw).facet("keywords")

        keywords = []

        for term, count in sqs.facet_counts()['fields']['keywords']:
            if term.startswith(kw):
                keywords.append((term, count))

        sorted(keywords, lambda x, y: cmp(x[1], y[1]))

        results = []

        for label, count in keywords:
            results.append({"label": label, "value": label})

        return HttpResponse(
            json.dumps(results),
            mimetype='application/json')



#####
##### Step 1: Create your newsletter model (see example below) and add it to your own project.
#####
# from django.db import models
# from ecl_tools.bulkmail.models import TrackingEvent, BaseBulkmailModel
#
# class NewsletterSample(BaseBulkmailModel):
#     title = models.CharField(max_length=60)
#
#     def StatsLink(self):
#         return '<a href="/bm/stats/'+str(self.id)+'">Stats</a>'
#     StatsLink.allow_tags = True
#
#     def get_subject(self):
#         return self.title
#
#     def utm_source(self):
#         return 'newsletter'
#
#     def get_campaign_id(self):
#         return 'newsletter_%d' % (
#             self.id)

#####
##### Step 2: Create your own CampaignResolver which returns the model associated with a particular campaign.
#####

class CampaignResolver(object):

    def get_model(self):
        #Return model which is your Newsletter and inherits from BaseBulkmailModel
        #return NewsletterSample
        raise Exception('Bulkmail improperly configured: You need to add BULKMAIL_CAMPAIGN_RESOLVER to your settings and it must conform to the example in ecl_tools.bulkmail.stats.example')

    def get(self, *args, **kwargs):

        #Return object for which we wish to retrieve stats.
        #return NewsletterSample.objects.get(id=kwargs['pk'])

        raise Exception('Bulkmail improperly configured: You need to add BULKMAIL_CAMPAIGN_RESOLVER to your settings and it must conform to the example in ecl_tools.bulkmail.stats.example')

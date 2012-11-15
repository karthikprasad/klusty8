#!/usr/bin/env python

###
# klusty8
#   - a serach result clustering application
#
# @author: karthikprasad
# @date: 13 Nov 2012
#        14 Nov 2012
#
###

import cluster as c
import collections as coll
import feedparser as fp
import webapp2
import jinja2
import os


jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinjaEnv.get_template("./templates/index.html")
        self.response.out.write(template.render())


class Search(webapp2.RequestHandler):
    def get(self):

    	feed_url = "http://www.bing.com/search?format=rss&count=50&q=" + self.request.get("q")
    	feed = fp.parse(feed_url)

    	K = 8
    	TH = 0.83
    	distanceMatrix = c.build_dist_matrix(feed["items"], c.jaccard_distance)

    	clusters = c.kmedoids(feed["items"], distanceMatrix, K, TH)

        orderedClusters = coll.OrderedDict(sorted(clusters.items(), key = lambda x: len(x[1]), reverse=True ))

    	templateValues = {"titles" : [],
    					  "clusters" : {},
                          "colours" : ["#FCF8E3","#F2DEDE","#DFF0D8","#FFCC66","#FFCCFF","#D9EDF7","#FFFCCC","#AFEEEE","#E6E6FA"]
                         }

    	for medoid, cluster in orderedClusters.iteritems():
    		templateValues["titles"].append(medoid["title"])
    		templateValues["clusters"][medoid["title"]] = cluster


    	template = jinjaEnv.get_template("./templates/cluster_divs.html")
        self.response.out.write(template.render(templateValues))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        template = jinjaEnv.get_template("./templates/about.html")
        self.response.out.write(template.render())


app = webapp2.WSGIApplication([("/", MainPage),
                               ("/about", AboutPage),
                               ("/search.*", Search)
                              ],
                               debug=True
                             )


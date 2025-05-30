from craigslist_meta import Site
import pycraigslist
from os import path

DEFAULT_SITE:str = 'chicago'


if __name__ == '__main__':
    
    paid_gigs = pycraigslist.gigs(site="portland", is_paid=True)
for gig in paid_gigs.search():
    print(gig)










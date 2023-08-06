from base_section import BaseSection

try: 
    from mtools.util.profile_collection import ProfileCollection
except ImportError:
    ProfileCollection = None

class RestartSection(BaseSection):
    """ This section determines if there were any restarts in the log file and prints out
        the times and version of the restarts found. It uses the information collected in
        LogFile so it doesn't have to walk the file manually.
    """
    
    name = "restarts"

    def __init__(self, mloginfo):
        BaseSection.__init__(self, mloginfo)

        # add --restarts flag to argparser
        self.mloginfo.argparser_sectiongroup.add_argument('--restarts', action='store_true', help='outputs information about every detected restart')


    @property
    def active(self):
        """ return boolean if this section is active. """
        return self.mloginfo.args['restarts']


    def run(self):

        if ProfileCollection and isinstance(self.mloginfo.logfile, ProfileCollection):
            print
            print "    not available for system.profile collections"
            print
            return

        """ run this section and print out information. """
        for version, logevent in self.mloginfo.logfile.restarts:
            print "   %s version %s" % (logevent.datetime.strftime("%b %d %H:%M:%S"), version)

        if len(self.mloginfo.logfile.restarts) == 0:
            print "  no restarts found"

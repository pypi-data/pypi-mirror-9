class Utils(object):

    durations = [64,48,32,24,16,16,16,16,16,16,12,8,8,8,6,4,4,2]
    print_durations = ['1','2.','2','4.','4','4','4','4','4','4','8.','8','8','8','16.','16','16','32']


    @classmethod
    def findDuration(self,duration):
        try:
            idx = self.durations.index(duration)
            return self.print_durations[idx]
        except:
            print "Duration %d not in list" % duration
            return ""

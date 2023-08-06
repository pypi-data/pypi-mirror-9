class MAT:
    # MAT module
    def __init__(self):
        # Use self.catalog and definitions
        pass

    def cal_longeststring(self, sample):
        import re

        # Determine the longest string in the sample to determine obfuscated code
        longeststring = 0

        words = re.split("[s,n,r]", sample)
        if words:
            for word in words:
                if len(word) > longeststring:
                    longeststring = len(word)

        return longeststring

    def cal_entropy(self, sample):
        import math

        # (Claude E.) Shannon entropy check. Determine uncertainty of the sample to detect encrypted code
        entropy = 0
        #try:
        for x in range(256):
            if len(sample) > 0:
                p_x = float(sample.count(chr(x)))/len(sample)
                if p_x > 0:
                    entropy += - p_x * math.log(p_x, 2)
        #except Exception, e:
        #    pass

        return entropy
import numpy
import os
import math
import logging
import Levenshtein

class Utils(object):

    @classmethod
    def load_data(cls, data_handle):
        """Load data from a file handle

        Must be tab delimited.
        """
        data = numpy.genfromtxt(data_handle, delimiter='\t', dtype=None, names=('id', 'data'))
        return data

    @classmethod
    def load_data_with_headers(file_handle):
        """Load data from file_handle, returning a header and body data.
        """
        data = file_handle.readlines()
        header = data[0].split('\t')
        body = [x.strip().split('\t') for x in data[1:]]
        return (header, body)

class Transforms(object):
    @classmethod
    def apply_reshape(cls, data, squash, offset):
        return (data * squash) + offset

    @classmethod
    def calculate_reshape(cls, data, newmin, newmax):
        squash = abs(newmax-newmin) / numpy.abs(numpy.max(data) - numpy.min(data))
        offset =  newmin - squash * numpy.min(data)
        return (squash, offset)

    @classmethod
    def apply_transform(cls, data, transform=None):
        if transform == 'none' or transform is None:
            return data
        elif transform == 'neg':
            return -data
        elif transform == 'log':
            return numpy.log10(data)
        elif transform == 'ln':
            return numpy.log(data)
        elif transform == 'inv':
            return 1/data
        elif transform == 'abs':
            return numpy.abs(data)
        else:
            raise NotImplementedError("Unknown transformation type %s" % transform)

class Cassettes(object):

    @classmethod
    def revcomrot(cls, cid):
        a = cls.rot(cid)
        b = cls.rot(cls.revcom(cid))
        return a+b

    @classmethod
    def revcom(cls, cid):
        cid = cid[::-1]
        cid = cid.replace('-', '.').replace('+', '-').replace('.', '-')
        return cid

    @classmethod
    def rot(cls, cid):
        results = []
        for i in range(len(cid)/2):
            results.append(cid[2*i:] + cid[0:2*i])
        return results


    @classmethod
    def collapse(cls, packed_cid):
        if len(packed_cid) < 4:
            return None

        unpacked_cid = [packed_cid[i:i+2] for i in range(0, len(packed_cid), 2)]
        o = cls.operons(unpacked_cid)
        reduced = [algo(x) for x in o]
        if reduced is not None:
            mod = ''.join([''.join(x) for x in reduced])
            return mod
        return None


    @classmethod
    def algo(cls, unpacked_cids):
        return cls.rmrep(unpacked_cids)


    @classmethod
    def rmrep(cls, unpacked_cids):
        f = []
        last = ""
        for x in unpacked_cids:
            if x != last:
                last = x
                f.append(x)
        return f

    @classmethod
    def operons(cls, unpacked_cid):
        o = []
        current_sign = ''
        c = []
        for pair in unpacked_cid:
            if pair[0] == current_sign:
                c.append(pair)
            else:
                if len(c) > 0:
                    o.append([x for x in c])
                    c = []

                current_sign = pair[0]
                c.append(pair)
        o.append([x for x in c])
        return o

    @classmethod
    def get_clustering_data(cls):
        module_dir, module_file = os.path.split(__file__)
        DATA_PATH = os.path.join(module_dir, 'data', 'clustering.yaml')
        with open(DATA_PATH, 'r') as handle:
            return yaml.load(handle)

class Clustering(object):

    @classmethod
    def meanshift(cls, data):
        from sklearn.cluster import MeanShift, estimate_bandwidth
        tmpdata = numpy.array(zip(data, numpy.zeros(len(data))))
        bandwidth = estimate_bandwidth(tmpdata)
        ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
        ms.fit(tmpdata)
        labels = ms.labels_
        cluster_centers = ms.cluster_centers_

        labels_unique = numpy.unique(labels)
        n_clusters_ = len(labels_unique)

        return labels

    @classmethod
    def user_break(cls, data, breaks=None, exact=False):
        ob = sorted(breaks)
        updated_data = []

        if not exact:
            labels = range(len(ob)+1)
            for i, data_point in enumerate(data):
                if data_point < ob[0]:
                    updated_data.append(labels[0])
                elif data_point >= ob[-1]:
                    updated_data.append(labels[-1])
                else:
                    hit = None
                    for i in range(len(ob)-1):
                        if ob[i] <= data_point < ob[i+1]:
                            hit = labels[i+1]
                    updated_data.append(hit)
                #print "%s -> %s" % (data_point, data[i])
        else:
            labels = range(len(ob))
            for i, data_point in enumerate(data):
                if data_point == ob[-1]:
                    updated_data.append(labels[-1])
                else:
                    hit = None
                    for i in range(len(ob)-1):
                        if ob[i] <= data_point < ob[i+1]:
                            hit = labels[i]
                    updated_data.append(hit)
                    if hit is None:
                        print hit, data_point
                #print "%s -> %s" % (data_point, data[i])
        return numpy.array(updated_data)

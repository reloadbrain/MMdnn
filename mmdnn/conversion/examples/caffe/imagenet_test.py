#----------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License.txt in the project root for license information.
#----------------------------------------------------------------------------------------------

import argparse
import numpy as np
import sys
import os
from six import text_type as _text_type
from mmdnn.conversion.examples.imagenet_test import TestKit
import caffe


class TestCaffe(TestKit):

    def __init__(self):
        super(TestCaffe, self).__init__()

        self.truth['caffe']['alexnet'] = [(657, 0.41121054), (744, 0.20789708), (847, 0.086725503), (821, 0.05908291), (595, 0.058017164)]

        if self.args.dump:
            self.dump_net = self.args.dump + '.prototxt'
            self.dump_weight = self.args.dump + '.caffemodel'
        else:
            self.dump_net = 'tmp.prototxt'
            self.dump_weight = 'tmp.caffemodel'

        self.MainModel.make_net(self.dump_net)
        self.MainModel.gen_weight(self.args.w, self.dump_weight, self.dump_net)
        self.model = caffe.Net(self.dump_net, self.dump_weight, caffe.TEST)

    def preprocess(self, image_path):
        x = super(TestCaffe, self).preprocess(image_path)
        # caffe uses NCHW
        x = np.transpose(x, [2, 0, 1])
        self.data = np.expand_dims(x, 0)


    def print_result(self):
        self.model.blobs['data'].data[...] = self.data
        if 'prob' in self.model.blobs:
            predict = self.model.forward()['prob'][0]
        else:
            predict = self.model.forward()['softmax'][0]
        super(TestCaffe, self).print_result(predict)


    def print_intermediate_result(self, layer_name, if_transpose = False):
        intermediate_output = self.model.blobs[layer_name].data[0]
        super(TestCaffe, self).print_intermediate_result(intermediate_output, if_transpose)


    def inference(self, image_path):
        self.preprocess(image_path)

        self.print_result()

        # self.print_intermediate_result('pooling0', False)

        self.test_truth()

        # delete tmp model files
        if os.path.isfile(self.dump_net):
            os.remove(self.dump_net)
        if os.path.isfile(self.dump_weight):
            os.remove(self.dump_weight)


    def dump(self):
        print ('Caffe model files are saved as [{}] and [{}], generated by [{}.py] and [{}].'.format(
            self.dump_net, self.dump_weight, self.args.n, self.args.w))


if __name__=='__main__':
    tester = TestCaffe()
    if tester.args.dump:
        tester.dump()
    else:
        tester.inference(tester.args.image)

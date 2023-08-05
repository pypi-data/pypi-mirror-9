# Copyright (c) 2009-2014 Stefan Marr <http://www.stefan-marr.de/>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import re
from .adapter         import GaugeAdapter, OutputNotParseable,\
    ResultsIndicatedAsInvalid
from ..model.data_point  import DataPoint
from ..model.measurement import Measurement


class CaliperAdapter(GaugeAdapter):
    """CaliperPerformance parses the output of Caliper with
       the ReBenchConsoleResultProcessor.
    """
    re_log_line = re.compile(r"Measurement \(runtime\) for (.*?) in (.*?): (.*?)ns")

    def check_for_error(self, line):
        ## for the moment we will simply not check for errors, because
        ## there are to many simple Error strings referring to class names
        ## TODO: find better solution
        pass

    def parse_data(self, data, run_id):
        data_points = []

        for line in data.split("\n"):
            if self.check_for_error(line):
                raise ResultsIndicatedAsInvalid(
                    "Output of bench program indicates errors.")

            m = self.re_log_line.match(line)
            if m:
                time = float(m.group(3)) / 1000000
                current = DataPoint(run_id)
                current.add_measurement(Measurement(time, 'ms', run_id,
                                                    criterion = m.group(1)))
                current.add_measurement(Measurement(time, 'ms', run_id,
                                                    criterion = 'total'))
                data_points.append(current)
        if len(data_points) == 0:
            raise OutputNotParseable(data)

        return data_points

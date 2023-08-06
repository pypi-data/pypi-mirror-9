###############################################################################
#
#   Onyx Portfolio & Risk Management Framework
#
#   Copyright 2014 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

__all__ = ["DailyCache"]

import datetime


###############################################################################
class DailyCache(dict):
    """
    This class provides unlimited caching with automatic refresh at the end
    of each day.
    """
    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.date = datetime.date.today()

    # -------------------------------------------------------------------------
    def __getitem__(self, *args, **kwds):
        if datetime.date.today() > self.date:
            self.date = datetime.date.today()
            self.clear()
        return super().__getitem__(*args, **kwds)

    # -------------------------------------------------------------------------
    def __contains__(self, *args, **kwds):
        if datetime.date.today() > self.date:
            self.date = datetime.date.today()
            self.clear()
        return super().__contains__(*args, **kwds)

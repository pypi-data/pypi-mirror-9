# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import aiohttp

from ..web.route import Route
from ..config import Config


class ShutdownHandler:

    @classmethod
    @Route.post(
        r"/shutdown",
        description="Shutdown the local server on Windows",
        api_version=None
    )
    def shutdown(request, response):

        server_config = Config.instance().get_section_config("Server")
        if server_config.get("local", False) is False:
            raise aiohttp.web.HTTPForbidden(text="You can only shutdown a local server")

        pass

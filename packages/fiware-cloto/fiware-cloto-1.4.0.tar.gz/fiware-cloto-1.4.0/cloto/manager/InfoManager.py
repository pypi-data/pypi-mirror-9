#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
__author__ = 'gjp'
import cloto.information as information
from cloto.models import TenantInfo, ServerInfo
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
import logging as logger


class InfoManager():
    """This class provides methods to manage information about the server and windowsize of tenants.
    """

    def __init__(self):
        self.tenantInfo = self.get_tenant_information()
        self.serverInfo = self.get_server_information()

    def get_server_information(self):
        """Returns model of Information about server."""
        return ServerInfo

    def get_tenant_information(self):
        """Returns model of Information about a tenant."""
        return TenantInfo

    def get_information(self, tenantId):
        """Returns information about the server and tenant's windowsize."""
        serverInfo = self.get_server_information()
        tenantInfo = self.get_tenant_information()
        s_query = serverInfo.objects.get(id__exact='1')
        t_query = tenantInfo.objects.get(tenantId__exact=tenantId)
        owner = s_query.__getattribute__("owner")
        windowsize = t_query.__getattribute__("windowsize")
        version = s_query.__getattribute__("version")
        runningfrom = s_query.__getattribute__("runningfrom")
        doc = s_query.__getattribute__("doc")
        return information.information(owner, windowsize, version, runningfrom, doc)

    def updateWindowSize(self, tenantId, newSize):
        """Updates windowsize of a specified tenant."""
        self.checkSize(newSize)
        t = self.tenantInfo.objects.get(tenantId__exact=tenantId)
        t.windowsize = newSize
        t.save()
        logger.info("%s windowsize updated to %d" % (tenantId, newSize))
        return t

    def setInformations(self, sInfo, tInfo):
        """Sets server information and tenant information to the InfoManager."""
        self.tenantInfo = tInfo
        self.serverInfo = sInfo

    def checkSize(self, newSize):
            if newSize <= 0 or newSize > settings.MAX_WINDOW_SIZE:
                raise ValidationError("New size is not an integer between 1 and %d" % settings.MAX_WINDOW_SIZE)

    def init_information(self):
        """Creates initial data in data base."""
        import datetime
        from django.utils import timezone
        from cloto.models import ServerInfo

        runningfrom = datetime.datetime.now(tz=timezone.get_default_timezone())
        # Creating initial data
        s = ServerInfo(id=1, owner=settings.OWNER, version=settings.VERSION,
                       runningfrom=runningfrom, doc=settings.API_INFO_URL)
        s.save()
